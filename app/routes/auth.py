from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user import AppUser
from app.models import db
import hashlib

auth_bp = Blueprint('auth', __name__)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_id = data.get('user_id', '')
    password = data.get('password', '')
    user = AppUser.query.get(user_id)
    if user and user.password_hash == hash_password(password):
        token = create_access_token(identity=user_id, additional_claims={'role': user.role or 'user'})
        return jsonify({'token': token, 'user': {'user_id': user.user_id, 'name': user.name, 'role': user.role}})
    return jsonify({'error': '用户名或密码错误'}), 401


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if AppUser.query.get(data.get('user_id', '')):
        return jsonify({'error': '用户ID已存在'}), 400
    user = AppUser(
        user_id=data['user_id'], name=data.get('name', ''), password_hash=hash_password(data.get('password', '')),
        role='user', review_count=0, useful=0, funny=0, cool=0, fans=0, average_stars=0
    )
    db.session.add(user)
    db.session.commit()
    token = create_access_token(identity=user.user_id, additional_claims={'role': 'user'})
    return jsonify({'token': token, 'user': {'user_id': user.user_id, 'name': user.name, 'role': 'user'}})


@auth_bp.route('/merchant-login', methods=['POST'])
def merchant_login():
    data = request.get_json()
    biz = AppUser.query.filter_by(user_id=data.get('business_id', ''), role='merchant').first()
    if biz and biz.password_hash == hash_password(data.get('password', '')):
        token = create_access_token(identity=biz.user_id, additional_claims={'role': 'merchant'})
        return jsonify({'token': token, 'user': {'user_id': biz.user_id, 'name': biz.name}})
    return jsonify({'error': '商家验证失败'}), 401


@auth_bp.route('/admin-login', methods=['POST'])
def admin_login():
    data = request.get_json()
    admin = AppUser.query.filter_by(user_id=data.get('user_id', ''), role='admin').first()
    if admin and admin.password_hash == hash_password(data.get('password', '')):
        token = create_access_token(identity=admin.user_id, additional_claims={'role': 'admin'})
        return jsonify({'token': token, 'user': {'user_id': admin.user_id, 'name': admin.name}})
    return jsonify({'error': '管理员验证失败'}), 401


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = AppUser.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    return jsonify({
        'user_id': user.user_id, 'name': user.name, 'review_count': user.review_count,
        'useful': user.useful, 'funny': user.funny, 'cool': user.cool,
        'fans': user.fans, 'average_stars': user.average_stars, 'role': user.role
    })