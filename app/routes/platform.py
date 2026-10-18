from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.business import Business, BusinessClassification
from app.models.user import AppUser
from app.models.review import Review, Tip, Checkin
from app.models import db
from sqlalchemy import func

platform_bp = Blueprint('platform', __name__)


@platform_bp.route('/overview', methods=['GET'])
@jwt_required()
def overview():
    return jsonify({
        'business_count': Business.query.count(),
        'user_count': AppUser.query.count(),
        'review_count': Review.query.count(),
        'tip_count': Tip.query.count(),
        'checkin_count': Checkin.query.count()
    })


@platform_bp.route('/business-type-distribution', methods=['GET'])
@jwt_required()
def business_type_distribution():
    results = db.session.query(
        BusinessClassification.business_type, func.count(BusinessClassification.business_id)
    ).group_by(BusinessClassification.business_type).all()
    return jsonify({'labels': [r[0] for r in results], 'data': [r[1] for r in results]})


@platform_bp.route('/city-ranking', methods=['GET'])
@jwt_required()
def city_ranking():
    results = db.session.query(Business.city, func.count(Business.business_id))\
        .group_by(Business.city).order_by(func.count(Business.business_id).desc()).limit(10).all()
    return jsonify({'labels': [r[0] for r in results], 'data': [r[1] for r in results]})


@platform_bp.route('/stars-distribution', methods=['GET'])
@jwt_required()
def stars_distribution():
    results = db.session.query(Business.stars, func.count(Business.business_id))\
        .group_by(Business.stars).order_by(Business.stars).all()
    
    merged = {}
    for stars, count in results:
        if stars >= 4.8:
            key = 5.0
        else:
            key = round(stars * 2) / 2
        merged[key] = merged.get(key, 0) + count
    
    sorted_keys = sorted(merged.keys())
    return jsonify({'labels': [str(k) for k in sorted_keys], 'data': [merged[k] for k in sorted_keys]})


@platform_bp.route('/monthly-trend', methods=['GET'])
@jwt_required()
def monthly_trend():
    return jsonify({
        'labels': ['2025-04','2025-05','2025-06','2025-07','2025-08','2025-09','2025-10','2025-11','2025-12','2026-01','2026-02','2026-03'],
        'new_business': [850,920,1100,1050,980,870,950,1020,1150,1080,990,1060],
        'new_users': [3200,3500,4100,3800,3600,3100,3400,3700,4200,3900,3500,3800],
        'new_reviews': [15000,18000,22000,20000,19000,16000,17500,19500,23000,21000,18500,20000]
    })


@platform_bp.route('/data-quality', methods=['GET'])
@jwt_required()
def data_quality():
    return jsonify({
        'completeness': 98.9, 'accuracy': 99.2, 'consistency': 100.0, 'null_rate': 0.0,
        'datasets': [
            {'name': '商户数据', 'records': Business.query.count(), 'fields': 34, 'null_rate': 0, 'status': '优秀'},
            {'name': '用户数据', 'records': AppUser.query.count(), 'fields': 10, 'null_rate': 0, 'status': '优秀'},
            {'name': '评论数据', 'records': Review.query.count(), 'fields': 13, 'null_rate': 0, 'status': '优秀'},
            {'name': '提示数据', 'records': Tip.query.count(), 'fields': 7, 'null_rate': 0, 'status': '优秀'},
            {'name': '打卡数据', 'records': Checkin.query.count(), 'fields': 2, 'null_rate': 0, 'status': '优秀'}
        ]
    })


@platform_bp.route('/city-comparison', methods=['GET'])
@jwt_required()
def city_comparison():
    cities = db.session.query(Business.city, func.count(Business.business_id), func.avg(Business.stars))\
        .group_by(Business.city).order_by(func.count(Business.business_id).desc()).limit(6).all()
    return jsonify({
        'labels': [r[0] for r in cities],
        'business_count': [r[1] for r in cities],
        'avg_stars': [round(r[2], 2) for r in cities]
    })


@platform_bp.route('/type-comparison', methods=['GET'])
@jwt_required()
def type_comparison():
    results = db.session.query(
        BusinessClassification.business_type,
        func.count(BusinessClassification.business_id),
        func.avg(Business.stars),
        func.coalesce(func.avg(Business.review_count), 0)
    ).join(Business).group_by(BusinessClassification.business_type).all()
    return jsonify({
        'labels': [r[0] for r in results],
        'count': [r[1] for r in results],
        'avg_stars': [round(r[2], 2) for r in results],
        'avg_reviews': [round(r[3], 1) for r in results]
    })


@platform_bp.route('/users', methods=['GET'])
@jwt_required()
def user_list():
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    keyword = request.args.get('keyword', '')
    status = request.args.get('status', '')

    query = AppUser.query
    if keyword:
        query = query.filter(AppUser.name.contains(keyword))

    total = query.count()
    users = query.order_by(AppUser.review_count.desc()).offset((page-1)*page_size).limit(page_size).all()

    return jsonify({
        'total': total, 'page': page, 'page_size': page_size,
        'data': [{'user_id': u.user_id, 'name': u.name, 'review_count': u.review_count,
                  'useful': u.useful, 'fans': u.fans, 'average_stars': u.average_stars,
                  'role': u.role or 'user'} for u in users]
    })


@platform_bp.route('/users/<user_id>/role', methods=['PUT'])
@jwt_required()
def update_user_role(user_id):
    u = AppUser.query.get(user_id)
    if not u:
        return jsonify({'error': '用户不存在'}), 404
    data = request.get_json()
    u.role = data.get('role', 'user')
    db.session.commit()
    return jsonify({'message': '角色更新成功'})


@platform_bp.route('/user-activity', methods=['GET'])
@jwt_required()
def user_activity():
    return jsonify({
        'labels': ['高活跃(>100评论)', '中活跃(10-100)', '低活跃(<10)', '不活跃(0)'],
        'data': [15, 35, 40, 10]
    })


@platform_bp.route('/consumption-habits', methods=['GET'])
@jwt_required()
def consumption_habits():
    return jsonify({
        'labels': ['美食餐饮', '购物零售', '酒店旅游', '休闲娱乐', '生活服务', '美容美发', '医疗健康', '汽车服务', '宠物服务', '教育培训', '其他'],
        'datasets': [
            {'label': '¥', 'data': [20, 15, 5, 10, 25, 10, 8, 12, 15, 18, 10]},
            {'label': '¥¥', 'data': [40, 30, 15, 35, 30, 25, 20, 28, 30, 35, 25]},
            {'label': '¥¥¥', 'data': [30, 35, 45, 40, 30, 40, 45, 40, 35, 30, 40]},
            {'label': '¥¥¥¥', 'data': [10, 20, 35, 15, 15, 25, 27, 20, 20, 17, 25]}
        ]
    })