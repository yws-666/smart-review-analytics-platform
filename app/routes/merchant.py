from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.business import Business
from app.models.review import Review
from app.models import db
from sqlalchemy import func
from collections import Counter

merchant_bp = Blueprint('merchant', __name__)


@merchant_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    biz_id = request.args.get('business_id', get_jwt_identity())
    b = Business.query.get(biz_id)
    if not b:
        return jsonify({'error': '商户不存在'}), 404

    review_count = Review.query.filter_by(business_id=biz_id).count()
    total_useful = db.session.query(func.sum(Review.useful)).filter(Review.business_id == biz_id).scalar() or 0

    return jsonify({
        'stars': b.stars, 'review_count': review_count, 'total_useful': total_useful,
        'visit_count': review_count * 15
    })


@merchant_bp.route('/review-trend', methods=['GET'])
@jwt_required()
def review_trend():
    biz_id = request.args.get('business_id', get_jwt_identity())
    results = db.session.query(Review.year, Review.month, func.count(Review.review_id))\
        .filter(Review.business_id == biz_id)\
        .group_by(Review.year, Review.month).order_by(Review.year, Review.month).all()
    return jsonify([{'year': r[0], 'month': r[1], 'count': r[2]} for r in results])


@merchant_bp.route('/rating-distribution', methods=['GET'])
@jwt_required()
def rating_distribution():
    biz_id = request.args.get('business_id', get_jwt_identity())
    results = db.session.query(Review.stars, func.count(Review.review_id))\
        .filter(Review.business_id == biz_id)\
        .group_by(Review.stars).order_by(Review.stars).all()
    return jsonify([{'stars': r[0], 'count': r[1]} for r in results])


@merchant_bp.route('/interaction-trend', methods=['GET'])
@jwt_required()
def interaction_trend():
    biz_id = request.args.get('business_id', get_jwt_identity())
    results = db.session.query(
        Review.year, Review.month,
        func.sum(Review.useful), func.sum(Review.funny), func.sum(Review.cool)
    ).filter(Review.business_id == biz_id)\
     .group_by(Review.year, Review.month).order_by(Review.year, Review.month).all()
    return jsonify([{'year': r[0], 'month': r[1], 'useful': r[2] or 0,
                     'funny': r[3] or 0, 'cool': r[4] or 0} for r in results])


@merchant_bp.route('/rating-radar', methods=['GET'])
@jwt_required()
def rating_radar():
    return jsonify({
        'taste': 4.2, 'environment': 3.8, 'service': 4.0, 'value': 3.9, 'location': 3.5, 'atmosphere': 4.1,
        'average': {'taste': 3.8, 'environment': 3.6, 'service': 3.7, 'value': 3.5, 'location': 3.4, 'atmosphere': 3.6}
    })


@merchant_bp.route('/sentiment-trend', methods=['GET'])
@jwt_required()
def sentiment_trend():
    return jsonify({
        'labels': ['2025-10', '2025-11', '2025-12', '2026-01', '2026-02', '2026-03', '2026-04'],
        'positive': [65, 68, 70, 72, 75, 78, 80],
        'neutral': [25, 22, 20, 18, 17, 15, 14],
        'negative': [10, 10, 10, 10, 8, 7, 6]
    })


@merchant_bp.route('/wordcloud', methods=['GET'])
@jwt_required()
def wordcloud():
    biz_id = request.args.get('business_id', get_jwt_identity())
    reviews = Review.query.filter_by(business_id=biz_id).limit(200).all()
    words = []
    for r in reviews:
        if r.text_cleaned:
            words.extend(r.text_cleaned.split())
    counter = Counter(words)
    return jsonify([{'text': w, 'weight': c} for w, c in counter.most_common(50) if len(w) > 2])


@merchant_bp.route('/reviews', methods=['GET'])
@jwt_required()
def merchant_reviews():
    biz_id = request.args.get('business_id', get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    
    query = Review.query.filter_by(business_id=biz_id).order_by(Review.year.desc(), Review.month.desc(), Review.day.desc())
    total = query.count()
    reviews = query.offset((page-1)*page_size).limit(page_size).all()
    
    return jsonify({
        'total': total,
        'page': page,
        'page_size': page_size,
        'data': [{
            'review_id': r.review_id,
            'user_id': r.user_id,
            'stars': r.stars,
            'date': f'{r.year}-{str(r.month).zfill(2)}-{str(r.day).zfill(2)}' if r.year else '',
            'text': r.text,
            'useful': r.useful,
            'funny': r.funny,
            'cool': r.cool
        } for r in reviews]
    })


@merchant_bp.route('/info', methods=['GET'])
@jwt_required()
def merchant_info():
    biz_id = request.args.get('business_id', get_jwt_identity())
    b = Business.query.get(biz_id)
    if not b:
        return jsonify({'error': '商户不存在'}), 404
    return jsonify({
        'business_id': b.business_id, 'name': b.name, 'address': b.address,
        'city': b.city, 'state': b.state, 'postal_code': b.postal_code,
        'stars': b.stars, 'review_count': b.review_count, 'is_open': b.is_open,
        'categories': b.categories
    })


@merchant_bp.route('/info', methods=['PUT'])
@jwt_required()
def update_merchant_info():
    biz_id = request.args.get('business_id', get_jwt_identity())
    b = Business.query.get(biz_id)
    if not b:
        return jsonify({'error': '商户不存在'}), 404
    data = request.get_json()
    for field in ['name', 'address', 'city', 'state', 'postal_code']:
        if field in data:
            setattr(b, field, data[field])
    db.session.commit()
    return jsonify({'message': '更新成功'})