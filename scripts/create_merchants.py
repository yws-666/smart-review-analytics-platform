"""
创建商家测试账号脚本
"""
import os
import sys
import hashlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db
from app.models.business import Business
from app.models.user import AppUser

app = create_app()

def create_merchant_accounts():
    print('正在创建商家账号...')
    
    # 获取前5个商户作为测试商家
    businesses = Business.query.limit(5).all()
    
    count = 0
    for biz in businesses:
        # 检查是否已存在商家账号
        existing = AppUser.query.get(biz.business_id)
        if not existing:
            merchant = AppUser(
                user_id=biz.business_id,
                name=biz.name,
                password_hash=hashlib.sha256('123456'.encode()).hexdigest(),
                role='merchant',
                review_count=0, useful=0, funny=0, cool=0, fans=0
            )
            db.session.add(merchant)
            count += 1
            print(f'  [创建] {biz.business_id} - {biz.name}')
        else:
            # 更新为商家角色（如果之前是普通用户）
            existing.role = 'merchant'
            existing.password_hash = hashlib.sha256('123456'.encode()).hexdigest()
            count += 1
            print(f'  [更新] {biz.business_id} - {biz.name}')
    
    db.session.commit()
    print(f'\n商家账号创建完成！共 {count} 个账号')
    print(f'默认密码: 123456')

if __name__ == '__main__':
    with app.app_context():
        create_merchant_accounts()