from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import AppUser
from app.models.review import UserFavorite, BrowseHistory
from app.models import db
from datetime import datetime

user_bp = Blueprint('user', __name__)


@user_bp.route('/<user_id>', methods=['GET'])
def user_info(user_id):
    u = AppUser.query.get(user_id)
    if not u:
        return jsonify({'error': '用户不存在'}), 404
    return jsonify({
        'user_id': u.user_id, 'name': u.name, 'review_count': u.review_count,
        'useful': u.useful, 'funny': u.funny, 'cool': u.cool,
        'fans': u.fans, 'average_stars': u.average_stars,
        'yelping_since': str(u.yelping_since) if u.yelping_since else ''
    })


@user_bp.route('/<user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    if get_jwt_identity() != user_id:
        return jsonify({'error': '无权限'}), 403
    u = AppUser.query.get(user_id)
    if not u:
        return jsonify({'error': '用户不存在'}), 404
    data = request.get_json()
    if 'name' in data:
        u.name = data['name']
    if 'preferences' in data:
        u.preferences = data['preferences']
    db.session.commit()
    return jsonify({'message': '更新成功'})


@user_bp.route('/<user_id>/favorites', methods=['GET'])
def user_favorites(user_id):
    favs = UserFavorite.query.filter_by(user_id=user_id).order_by(UserFavorite.created_at.desc()).all()
    return jsonify([{
        'business_id': f.business_id,
        'business_name': f.business.name if f.business else '',
        'business_stars': f.business.stars if f.business else 0,
        'business_type': f.business.classification.business_type if f.business and f.business.classification else '其他',
        'created_at': str(f.created_at)
    } for f in favs])


@user_bp.route('/<user_id>/favorites', methods=['POST'])
def add_favorite(user_id):
    data = request.get_json()
    biz_id = data.get('business_id', '')
    if not biz_id:
        return jsonify({'error': '缺少business_id'}), 400
    exist = UserFavorite.query.filter_by(user_id=user_id, business_id=biz_id).first()
    if exist:
        return jsonify({'message': '已收藏'})
    fav = UserFavorite(user_id=user_id, business_id=biz_id, created_at=datetime.now())
    db.session.add(fav)
    db.session.commit()
    return jsonify({'message': '收藏成功'})


@user_bp.route('/<user_id>/favorites/<biz_id>', methods=['DELETE'])
def remove_favorite(user_id, biz_id):
    fav = UserFavorite.query.filter_by(user_id=user_id, business_id=biz_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
    return jsonify({'message': '取消收藏'})


@user_bp.route('/<user_id>/history', methods=['GET'])
def user_history(user_id):
    history = BrowseHistory.query.filter_by(user_id=user_id).order_by(BrowseHistory.browsed_at.desc()).limit(50).all()
    return jsonify([{
        'business_id': h.business_id,
        'business_name': h.business.name if h.business else '',
        'business_stars': h.business.stars if h.business else 0,
        'business_type': h.business.classification.business_type if h.business and h.business.classification else '其他',
        'browsed_at': str(h.browsed_at)
    } for h in history])


@user_bp.route('/<user_id>/history', methods=['POST'])
def add_history(user_id):
    data = request.get_json()
    biz_id = data.get('business_id', '')
    if not biz_id:
        return jsonify({'error': '缺少business_id'}), 400
    h = BrowseHistory(user_id=user_id, business_id=biz_id, browsed_at=datetime.now())
    db.session.add(h)
    db.session.commit()
    return jsonify({'message': '记录成功'})


@user_bp.route('/<user_id>/history/<biz_id>', methods=['DELETE'])
def remove_history(user_id, biz_id):
    history = BrowseHistory.query.filter_by(user_id=user_id, business_id=biz_id).first()
    if history:
        db.session.delete(history)
        db.session.commit()
    return jsonify({'message': '删除成功'})


@user_bp.route('/<user_id>/preferences', methods=['GET'])
def get_preferences(user_id):
    u = AppUser.query.get(user_id)
    if u and u.preferences:
        import json
        return jsonify(json.loads(u.preferences))
    return jsonify({'categories': [], 'price_range': [], 'min_stars': 0})


@user_bp.route('/<user_id>/preferences', methods=['PUT'])
def update_preferences(user_id):
    u = AppUser.query.get(user_id)
    if not u:
        return jsonify({'error': '用户不存在'}), 404
    data = request.get_json()
    import json
    u.preferences = json.dumps(data)
    db.session.commit()
    return jsonify({'message': '更新成功'})