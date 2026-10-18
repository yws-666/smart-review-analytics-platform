"""
智评优选 - 推荐算法模块（优化版）

实现三层推荐算法：
1. 基于用户偏好的推荐（优先）- 优化：批量查询
2. 协同过滤推荐（次优）- 优化：N+1查询消除
3. 基于内容的推荐（备选）- 优化：预加载分类

优化策略：
- 消除N+1查询问题，使用批量IN查询
- 预加载关联数据，减少数据库往返
- 限制计算规模，设置超时保护
- 基于用户偏好的推荐如果满足limit则跳过后续计算
"""

import math
import random
import time
from collections import defaultdict
from app.models.business import Business, BusinessClassification
from app.models.review import Review, UserFavorite, BrowseHistory
from app.models.user import AppUser
from app.models import db
from sqlalchemy import func

# 超时限制（秒）
MAX_COMPUTE_TIME = 1.5


def _format_business(biz):
    """快速序列化商户对象"""
    return biz


# ==========================================
# 1. 基于用户偏好的推荐（优化版）
# ==========================================

def get_preference_based_recommendations(user_id, limit=10):
    """
    根据用户偏好设置、收藏历史、浏览历史进行个性化推荐
    优化：使用单次查询获取分类数据
    """
    user = AppUser.query.get(user_id)
    if not user:
        return []
    
    # 批量获取用户交互过的商户ID
    interacted_ids = set()
    
    fav_ids = db.session.query(UserFavorite.business_id).filter_by(user_id=user_id).all()
    interacted_ids.update(row[0] for row in fav_ids)
    
    hist_ids = db.session.query(BrowseHistory.business_id).filter_by(user_id=user_id)\
        .order_by(BrowseHistory.browsed_at.desc()).limit(50).all()
    interacted_ids.update(row[0] for row in hist_ids)
    
    # 批量获取收藏商户的分类
    preferred_categories = set()
    if interacted_ids:
        cat_rows = db.session.query(BusinessClassification.business_type).filter(
            BusinessClassification.business_id.in_(list(interacted_ids)[:50])
        ).all()
        preferred_categories.update(row[0] for row in cat_rows)
    
    # 解析用户偏好设置
    import json
    user_prefs = {}
    if user.preferences:
        try:
            user_prefs = json.loads(user.preferences)
        except:
            pass
    
    pref_categories = set(user_prefs.get('categories', []))
    preferred_categories.update(pref_categories)
    pref_price = user_prefs.get('price_range', '')
    pref_min_stars = user_prefs.get('min_stars', 0)
    
    # 构建推荐查询
    min_stars = max(pref_min_stars, 3.5)
    query = Business.query.filter(Business.stars >= min_stars)
    if interacted_ids:
        query = query.filter(~Business.business_id.in_(list(interacted_ids)[:1000]))
    
    # 优先匹配偏好类别
    if preferred_categories:
        businesses = query.join(BusinessClassification).filter(
            BusinessClassification.business_type.in_(list(preferred_categories))
        ).order_by(Business.stars.desc(), Business.review_count.desc()).limit(limit * 2).all()
        if businesses:
            random.shuffle(businesses)
            return businesses[:limit]
    
    # 同价格区间
    if pref_price:
        businesses = query.filter(Business.attr_price_range == pref_price)\
            .order_by(Business.stars.desc(), Business.review_count.desc()).limit(limit * 2).all()
        if businesses:
            random.shuffle(businesses)
            return businesses[:limit]
    
    # 兜底
    businesses = query.order_by(Business.stars.desc(), Business.review_count.desc()).limit(limit * 2).all()
    random.shuffle(businesses)
    return businesses[:limit]


# ==========================================
# 2. 协同过滤推荐（优化版 - 消除N+1查询）
# ==========================================

def get_collaborative_filtering_recommendations(user_id, limit=10):
    """
    基于用户的协同过滤推荐（User-based Collaborative Filtering）
    优化：使用批量查询替代循环查询，减少数据库往返次数
    """
    start_time = time.time()
    
    # 获取目标用户评论过的商户
    target_reviews = Review.query.filter_by(user_id=user_id).all()
    if len(target_reviews) < 5:  # 提高最低要求，评论太少效果差且计算开销大
        return []
    
    target_reviewed = {r.business_id: r.stars for r in target_reviews}
    target_biz_ids = list(target_reviewed.keys())
    
    # 批量获取所有评论过这些商户的其他用户
    other_user_ids = db.session.query(Review.user_id).filter(
        Review.business_id.in_(target_biz_ids),
        Review.user_id != user_id
    ).distinct().limit(300).all()  # 降低到300，加速计算
    
    other_user_ids = [row[0] for row in other_user_ids]
    if not other_user_ids:
        return []
    
    # 【优化】批量获取所有相关评论，替代N次循环查询
    all_reviews = Review.query.filter(
        Review.user_id.in_(other_user_ids),
        Review.stars > 0
    ).all()
    
    # 构建用户评分向量字典
    user_vectors = {}
    for r in all_reviews:
        uid = r.user_id
        if uid not in user_vectors:
            user_vectors[uid] = {}
        user_vectors[uid][r.business_id] = r.stars
    
    # 过滤出至少有3条评论的用户
    user_vectors = {uid: vec for uid, vec in user_vectors.items() if len(vec) >= 3}
    
    # 计算余弦相似度
    def cosine_similarity(vec1, vec2):
        common_items = set(vec1.keys()) & set(vec2.keys())
        if len(common_items) < 2:  # 至少2个共同项才计算
            return 0.0
        sum_xy = sum(vec1[item] * vec2[item] for item in common_items)
        sum_x2 = sum(vec1[item] ** 2 for item in common_items)
        sum_y2 = sum(vec2[item] ** 2 for item in common_items)
        if sum_x2 == 0 or sum_y2 == 0:
            return 0.0
        return sum_xy / (math.sqrt(sum_x2) * math.sqrt(sum_y2))
    
    # 计算与目标用户的相似度
    similarities = {}
    for uid, vec in user_vectors.items():
        sim = cosine_similarity(target_reviewed, vec)
        if sim > 0.1:  # 只保留有显著相似度的用户
            similarities[uid] = sim
    
    # 选取Top-K相似用户
    sorted_sims = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:10]
    
    if not sorted_sims:
        return []
    
    # 预测评分
    candidates = defaultdict(float)
    candidate_weights = defaultdict(float)
    
    for similar_uid, sim in sorted_sims:
        for biz_id, rating in user_vectors[similar_uid].items():
            if biz_id not in target_reviewed:
                candidates[biz_id] += sim * rating
                candidate_weights[biz_id] += sim
    
    predicted_scores = {
        biz_id: candidates[biz_id] / candidate_weights[biz_id]
        for biz_id in candidates if candidate_weights[biz_id] > 0
    }
    
    if not predicted_scores:
        return []
    
    # 获取预测评分最高的商户 - 批量查询
    top_ids = sorted(predicted_scores.keys(), key=lambda x: predicted_scores[x], reverse=True)[:limit * 2]
    
    businesses = Business.query.filter(
        Business.business_id.in_(top_ids),
        Business.stars >= 3.5
    ).all()
    
    business_map = {b.business_id: b for b in businesses}
    sorted_businesses = [business_map[bid] for bid in top_ids if bid in business_map]
    
    # 超时检查
    elapsed = time.time() - start_time
    if elapsed > MAX_COMPUTE_TIME:
        return []  # 超时则不返回，让后续快速层补上
    
    return sorted_businesses[:limit]


# ==========================================
# 3. 基于内容的推荐（优化版 - 预加载分类）
# ==========================================

def get_content_based_recommendations(user_id, limit=10):
    """
    基于内容的推荐（Content-based Filtering）
    优化：预加载所有分类数据，消除N+1查询
    """
    start_time = time.time()
    
    # 获取用户交互过的商户
    interacted_ids = set()
    
    fav_ids = db.session.query(UserFavorite.business_id).filter_by(user_id=user_id).all()
    interacted_ids.update(row[0] for row in fav_ids)
    
    review_ids = db.session.query(Review.business_id).filter_by(user_id=user_id).all()
    interacted_ids.update(row[0] for row in review_ids)
    
    hist_ids = db.session.query(BrowseHistory.business_id).filter_by(user_id=user_id).limit(50).all()
    interacted_ids.update(row[0] for row in hist_ids)
    
    if not interacted_ids:
        return []
    
    # 【优化】批量获取商户信息和分类
    interacted_businesses = Business.query.filter(
        Business.business_id.in_(list(interacted_ids)[:200])
    ).all()
    
    if not interacted_businesses:
        return []
    
    # 【优化】批量获取所有分类数据，构建映射
    all_biz_ids = [b.business_id for b in interacted_businesses]
    classifications = db.session.query(
        BusinessClassification.business_id, BusinessClassification.business_type
    ).filter(BusinessClassification.business_id.in_(all_biz_ids)).all()
    biz_classification_map = {row[0]: row[1] for row in classifications}
    
    # 构建用户画像
    category_scores = defaultdict(float)
    city_scores = defaultdict(float)
    price_scores = defaultdict(float)
    
    for biz in interacted_businesses:
        biz_type = biz_classification_map.get(biz.business_id)
        if biz_type:
            category_scores[biz_type] += biz.stars
        
        if biz.city:
            city_scores[biz.city] += biz.stars
        
        if biz.attr_price_range:
            price_scores[biz.attr_price_range] += biz.stars
    
    # 归一化
    total_category = sum(category_scores.values()) or 1
    total_city = sum(city_scores.values()) or 1
    total_price = sum(price_scores.values()) or 1
    
    category_prefs = {k: v / total_category for k, v in category_scores.items()}
    city_prefs = {k: v / total_city for k, v in city_scores.items()}
    price_prefs = {k: v / total_price for k, v in price_scores.items()}
    
    # 获取候选商户
    candidate_businesses = Business.query.filter(
        Business.stars >= 3.5,
        ~Business.business_id.in_(list(interacted_ids)[:1000]) if interacted_ids else True
    ).limit(300).all()  # 减少候选数加速
    
    # 【优化】预加载候选商户的分类数据
    candidate_ids = [b.business_id for b in candidate_businesses]
    candidate_classifications = db.session.query(
        BusinessClassification.business_id, BusinessClassification.business_type
    ).filter(BusinessClassification.business_id.in_(candidate_ids)).all()
    candidate_biz_map = {row[0]: row[1] for row in candidate_classifications}
    
    # 计算匹配度
    scored_businesses = []
    for biz in candidate_businesses:
        score = 0.0
        weight_sum = 0.0
        
        biz_type = candidate_biz_map.get(biz.business_id)
        if biz_type and biz_type in category_prefs:
            score += 0.5 * category_prefs[biz_type]
            weight_sum += 0.5
        
        if biz.city in city_prefs:
            score += 0.3 * city_prefs[biz.city]
            weight_sum += 0.3
        
        if biz.attr_price_range in price_prefs:
            score += 0.2 * price_prefs[biz.attr_price_range]
            weight_sum += 0.2
        
        if weight_sum > 0:
            score /= weight_sum
            score = score * 0.6 + (biz.stars / 5.0) * 0.4
            scored_businesses.append((biz, score))
    
    scored_businesses.sort(key=lambda x: x[1], reverse=True)
    
    # 超时检查
    elapsed = time.time() - start_time
    if elapsed > MAX_COMPUTE_TIME:
        return []
    
    return [biz for biz, _ in scored_businesses[:limit]]


# ==========================================
# 主推荐接口 - 三层推荐融合（快速响应版）
# ==========================================

def get_recommendations(user_id, limit=10):
    """
    三层推荐融合策略（快速响应）：
    
    1. 优先：基于用户偏好（快速，直接查询）
    2. 次优：协同过滤（较慢，有超时保护）
    3. 备选：基于内容（较慢，有超时保护）
    4. 兜底：热门推荐（快速）
    """
    start_time = time.time()
    recommended_ids = set()
    results = []
    
    # 第1层：基于用户偏好（快速查询）
    pref_results = get_preference_based_recommendations(user_id, limit)
    for biz in pref_results:
        if biz.business_id not in recommended_ids:
            results.append(biz)
            recommended_ids.add(biz.business_id)
    
    if len(results) >= limit or (time.time() - start_time) > MAX_COMPUTE_TIME * 2:
        return results[:limit]
    
    # 第2层：协同过滤（有超时保护）
    cf_results = get_collaborative_filtering_recommendations(user_id, limit)
    for biz in cf_results:
        if biz.business_id not in recommended_ids:
            results.append(biz)
            recommended_ids.add(biz.business_id)
    
    if len(results) >= limit or (time.time() - start_time) > MAX_COMPUTE_TIME * 3:
        return results[:limit]
    
    # 第3层：基于内容（有超时保护）
    cb_results = get_content_based_recommendations(user_id, limit)
    for biz in cb_results:
        if biz.business_id not in recommended_ids:
            results.append(biz)
            recommended_ids.add(biz.business_id)
    
    # 兜底：全局热门推荐
    if len(results) < limit:
        fallback = Business.query.filter(
            Business.stars >= 4,
            Business.review_count >= 10,
            ~Business.business_id.in_(list(recommended_ids)[:500]) if recommended_ids else True
        ).order_by(Business.review_count.desc()).limit(limit - len(results)).all()
        
        for biz in fallback:
            if biz.business_id not in recommended_ids:
                results.append(biz)
                recommended_ids.add(biz.business_id)
    
    return results[:limit]
