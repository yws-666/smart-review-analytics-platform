from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.business import Business, BusinessClassification
from app.models.review import Review, Tip, Checkin, BrowseHistory, ReviewVote
from app.models.user import AppUser
from app.models import db
from sqlalchemy import func
from datetime import datetime

business_bp = Blueprint('business', __name__)


@business_bp.route('', methods=['GET'])
def list_businesses():
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    sort_by = request.args.get('sort', 'stars')
    order = request.args.get('order', 'desc')
    city = request.args.get('city', '')
    biz_type = request.args.get('type', '')
    keyword = request.args.get('keyword', '')
    min_stars = request.args.get('min_stars', 0, type=float)
    max_stars = request.args.get('max_stars', 5, type=float)
    price_range = request.args.get('price_range', '')

    query = Business.query
    if biz_type:
        query = query.join(BusinessClassification).filter(BusinessClassification.business_type == biz_type)
    if city:
        query = query.filter(Business.city == city)
    if keyword:
        query = query.filter(Business.name.contains(keyword))
    query = query.filter(Business.stars >= min_stars, Business.stars <= max_stars)
    if price_range:
        query = query.filter(Business.attr_price_range == price_range)

    sort_col = getattr(Business, sort_by, Business.stars)
    query = query.order_by(sort_col.desc() if order == 'desc' else sort_col.asc())

    total = query.count()
    businesses = query.offset((page - 1) * page_size).limit(page_size).all()

    return jsonify({
        'total': total, 'page': page, 'page_size': page_size,
        'data': [{'business_id': b.business_id, 'name': b.name, 'city': b.city, 'state': b.state,
                  'stars': b.stars, 'review_count': b.review_count, 'categories': b.categories,
                  'latitude': b.latitude, 'longitude': b.longitude, 'is_open': b.is_open,
                  'attr_price_range': b.attr_price_range,
                  'business_type': b.classification.business_type if b.classification else '其他'} for b in businesses]
    })


@business_bp.route('/<biz_id>', methods=['GET'])
def business_detail(biz_id):
    b = Business.query.get(biz_id)
    if not b:
        return jsonify({'error': '商户不存在'}), 404
    return jsonify({
        'business_id': b.business_id, 'name': b.name, 'address': b.address,
        'city': b.city, 'state': b.state, 'postal_code': b.postal_code,
        'latitude': b.latitude, 'longitude': b.longitude, 'stars': b.stars,
        'stars_normalized': b.stars_normalized, 'review_count': b.review_count,
        'is_open': b.is_open, 'categories': b.categories,
        'business_type': b.classification.business_type if b.classification else '其他',
        'attrs': {
            'accepts_credit_cards': b.attr_accepts_credit_cards,
            'bike_parking': b.attr_bike_parking, 'take_out': b.attr_take_out,
            'delivery': b.attr_delivery, 'good_for_kids': b.attr_good_for_kids,
            'outdoor_seating': b.attr_outdoor_seating, 'has_tv': b.attr_has_tv,
            'reservations': b.attr_reservations, 'caters': b.attr_caters,
            'good_for_groups': b.attr_good_for_groups, 'wheelchair': b.attr_wheelchair,
            'dogs_allowed': b.attr_dogs_allowed, 'table_service': b.attr_table_service,
            'happy_hour': b.attr_happy_hour, 'by_appointment': b.attr_by_appointment,
            'wifi': b.attr_wifi, 'alcohol': b.attr_alcohol, 'noise_level': b.attr_noise_level,
            'attire': b.attr_attire, 'price_range': b.attr_price_range
        }
    })


@business_bp.route('/search', methods=['GET'])
def search():
    return list_businesses()


@business_bp.route('/categories', methods=['GET'])
def categories():
    results = db.session.query(
        BusinessClassification.business_type, func.count(BusinessClassification.business_id)
    ).group_by(BusinessClassification.business_type).all()
    
    # 把"其他"放在最后
    categories_list = []
    others = None
    for r in results:
        if r[0] == '其他':
            others = {'type': r[0], 'count': r[1]}
        else:
            categories_list.append({'type': r[0], 'count': r[1]})
    
    # 添加"其他"到最后
    if others:
        categories_list.append(others)
    
    return jsonify(categories_list)


@business_bp.route('/hot', methods=['GET'])
def hot_businesses():
    limit = request.args.get('limit', 10, type=int)
    businesses = Business.query.filter(Business.stars >= 4, Business.review_count >= 10)\
        .order_by(Business.review_count.desc()).limit(limit).all()
    return jsonify([{'business_id': b.business_id, 'name': b.name, 'city': b.city,
                     'stars': b.stars, 'review_count': b.review_count,
                     'categories': b.categories, 'attr_price_range': b.attr_price_range} for b in businesses])


@business_bp.route('/recommend', methods=['GET'])
def recommend():
    """
    三层推荐算法接口：
    1. 优先：基于用户偏好（收藏/浏览/偏好设置）
    2. 次优：协同过滤（相似用户行为）
    3. 备选：基于内容（商户特征匹配）
    
    未登录用户使用全局热门推荐
    """
    limit = request.args.get('limit', 10, type=int)
    
    # 检查是否有JWT认证（已登录用户）
    try:
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
    except:
        user_id = None
    
    if user_id:
        # 已登录用户 - 使用三层推荐算法
        from app.recommender import get_recommendations
        businesses = get_recommendations(user_id, limit)
        algo_source = '个性化推荐（基于用户偏好+协同过滤+内容匹配）'
    else:
        # 未登录用户 - 使用全局热门推荐
        businesses = Business.query.filter(Business.stars >= 4, Business.review_count >= 10)\
            .order_by(Business.review_count.desc()).limit(limit).all()
        algo_source = '热门推荐'
    
    return jsonify([{'business_id': b.business_id, 'name': b.name, 'city': b.city,
                     'stars': b.stars, 'review_count': b.review_count,
                     'categories': b.categories, 'attr_price_range': b.attr_price_range} for b in businesses])


@business_bp.route('/<biz_id>/reviews', methods=['GET'])
def business_reviews(biz_id):
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    sort_by = request.args.get('sort', 'useful')

    query = Review.query.filter_by(business_id=biz_id)
    sort_col = getattr(Review, sort_by, Review.useful)
    query = query.order_by(sort_col.desc())

    total = query.count()
    reviews = query.offset((page - 1) * page_size).limit(page_size).all()

    return jsonify({
        'total': total, 'page': page, 'page_size': page_size,
        'data': [{'review_id': r.review_id, 'user_id': r.user_id, 'user_name': r.user.name if r.user else '',
                  'stars': r.stars, 'useful': r.useful, 'funny': r.funny, 'cool': r.cool,
                  'year': r.year, 'month': r.month, 'day': r.day, 'text': r.text} for r in reviews]
    })


@business_bp.route('/<biz_id>/tips', methods=['GET'])
def business_tips(biz_id):
    tips = Tip.query.filter_by(business_id=biz_id).order_by(Tip.compliment_count.desc()).limit(20).all()
    return jsonify([{'user_id': t.user_id, 'text': t.text, 'year': t.year,
                     'month': t.month, 'compliment_count': t.compliment_count} for t in tips])


@business_bp.route('/<biz_id>/checkins', methods=['GET'])
def business_checkins(biz_id):
    checkin = Checkin.query.filter_by(business_id=biz_id).first()
    return jsonify({'business_id': biz_id, 'date': checkin.date if checkin else ''})


@business_bp.route('/cities', methods=['GET'])
def cities():
    results = db.session.query(Business.city, func.count(Business.business_id))\
        .group_by(Business.city).order_by(func.count(Business.business_id).desc()).limit(20).all()
    return jsonify([{'city': r[0], 'count': r[1]} for r in results])


@business_bp.route('/<biz_id>/reviews', methods=['POST'])
@jwt_required()
def add_review(biz_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    stars = data.get('stars', 1)
    text = data.get('text', '')
    
    if stars < 1 or stars > 5:
        return jsonify({'error': '评分必须在1-5之间'}), 400
    
    today = datetime.now()
    review = Review(
        review_id=user_id[:10] + str(today.timestamp())[:10],
        user_id=user_id,
        business_id=biz_id,
        stars=stars,
        stars_normalized=(stars - 1) / 4,
        useful=0,
        funny=0,
        cool=0,
        year=today.year,
        month=today.month,
        day=today.day,
        text=text,
        text_cleaned=text[:200]
    )
    db.session.add(review)
    
    # 更新商户评分和评论数
    business = Business.query.get(biz_id)
    if business:
        business.review_count = (business.review_count or 0) + 1
        business.stars = ((business.stars or 0) * (business.review_count - 1) + stars) / business.review_count
    
    # 更新用户评论数和平均评分
    user = AppUser.query.get(user_id)
    if user:
        user.review_count = (user.review_count or 0) + 1
        user.average_stars = ((user.average_stars or 0) * (user.review_count - 1) + stars) / user.review_count
    
    db.session.commit()
    return jsonify({'message': '评论成功'})


@business_bp.route('/reviews/<review_id>/vote', methods=['POST'])
@jwt_required()
def vote_review(review_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    vote_type = data.get('type', 'useful')
    
    review = Review.query.get(review_id)
    if not review:
        return jsonify({'error': '评论不存在'}), 404
    
    # 检查用户是否已经投过票
    existing_vote = ReviewVote.query.filter_by(
        user_id=user_id, 
        review_id=review_id, 
        vote_type=vote_type
    ).first()
    
    if existing_vote:
        # 已投票，取消投票
        db.session.delete(existing_vote)
        if vote_type == 'useful':
            review.useful = max(0, (review.useful or 0) - 1)
        elif vote_type == 'funny':
            review.funny = max(0, (review.funny or 0) - 1)
        elif vote_type == 'cool':
            review.cool = max(0, (review.cool or 0) - 1)
        
        # 更新评论作者的统计数据
        author = AppUser.query.get(review.user_id)
        if author:
            if vote_type == 'useful':
                author.useful = max(0, (author.useful or 0) - 1)
            elif vote_type == 'funny':
                author.funny = max(0, (author.funny or 0) - 1)
            elif vote_type == 'cool':
                author.cool = max(0, (author.cool or 0) - 1)
        
        db.session.commit()
        return jsonify({'message': '取消投票成功', 'count': {
            'useful': review.useful,
            'funny': review.funny,
            'cool': review.cool
        }, 'voted': False})
    else:
        # 未投票，添加投票
        new_vote = ReviewVote(user_id=user_id, review_id=review_id, vote_type=vote_type)
        db.session.add(new_vote)
        
        if vote_type == 'useful':
            review.useful = (review.useful or 0) + 1
        elif vote_type == 'funny':
            review.funny = (review.funny or 0) + 1
        elif vote_type == 'cool':
            review.cool = (review.cool or 0) + 1
        
        # 更新评论作者的统计数据
        author = AppUser.query.get(review.user_id)
        if author:
            if vote_type == 'useful':
                author.useful = (author.useful or 0) + 1
            elif vote_type == 'funny':
                author.funny = (author.funny or 0) + 1
            elif vote_type == 'cool':
                author.cool = (author.cool or 0) + 1
        
        db.session.commit()
        return jsonify({'message': '投票成功', 'count': {
            'useful': review.useful,
            'funny': review.funny,
            'cool': review.cool
        }, 'voted': True})


@business_bp.route('/<biz_id>/history', methods=['POST'])
def add_browse_history(biz_id):
    data = request.get_json()
    user_id = data.get('user_id', '')
    
    if not user_id:
        return jsonify({'error': '用户ID不能为空'}), 400
    
    history = BrowseHistory(
        user_id=user_id,
        business_id=biz_id,
        browsed_at=datetime.now()
    )
    db.session.add(history)
    db.session.commit()
    return jsonify({'message': '记录成功'})


@business_bp.route('/reviews/<review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    user_id = get_jwt_identity()
    
    review = Review.query.get(review_id)
    if not review:
        return jsonify({'error': '评论不存在'}), 404
    
    # 检查是否是自己的评论
    if review.user_id != user_id:
        return jsonify({'error': '只能删除自己的评论'}), 403
    
    # 获取商户信息用于更新评分
    business = Business.query.get(review.business_id)
    
    try:
        # 删除评论相关的投票记录（有容错处理）
        ReviewVote.query.filter_by(review_id=review_id).delete()
    except:
        pass
    
    # 删除评论
    db.session.delete(review)
    
    # 更新商户评分和评论数
    if business:
        business.review_count = max(0, (business.review_count or 1) - 1)
        if business.review_count == 0:
            business.stars = 0
        else:
            # 重新计算商户评分
            avg_rating = db.session.query(func.avg(Review.stars)).filter_by(business_id=business.business_id).scalar()
            business.stars = avg_rating or 0
    
    # 更新用户评论数和平均评分
    user = AppUser.query.get(user_id)
    if user:
        user.review_count = max(0, (user.review_count or 1) - 1)
        if user.review_count == 0:
            user.average_stars = 0
        else:
            avg_stars = db.session.query(func.avg(Review.stars)).filter_by(user_id=user_id).scalar()
            user.average_stars = avg_stars or 0
    
    db.session.commit()
    return jsonify({'message': '删除成功'})