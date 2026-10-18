"""
数据库初始化脚本
从 processed_data/ 目录读取 CSV 文件，导入 SQLite 数据库
"""
import os
import sys
import pandas as pd
import hashlib
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db
from app.models.business import Business, BusinessClassification
from app.models.user import AppUser
from app.models.review import Review, Tip, Checkin

app = create_app()

PROCESSED_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'processed_data')


def import_business():
    print('导入商户数据...')
    filepath = os.path.join(PROCESSED_DIR, 'processed_business.csv')
    df = pd.read_csv(filepath)
    df = df.where(pd.notnull(df), None)

    for _, row in df.iterrows():
        try:
            biz = Business(
                business_id=row.get('business_id'),
                name=row.get('name'),
                address=row.get('address'),
                city=row.get('city'),
                state=row.get('state'),
                postal_code=row.get('postal_code'),
                latitude=row.get('latitude') if pd.notna(row.get('latitude')) else None,
                longitude=row.get('longitude') if pd.notna(row.get('longitude')) else None,
                stars=row.get('stars') if pd.notna(row.get('stars')) else None,
                stars_normalized=row.get('stars_normalized') if pd.notna(row.get('stars_normalized')) else None,
                review_count=row.get('review_count') if pd.notna(row.get('review_count')) else None,
                review_count_log=row.get('review_count_log') if pd.notna(row.get('review_count_log')) else None,
                is_open=row.get('is_open') if pd.notna(row.get('is_open')) else None,
                categories=row.get('categories'),
                attr_accepts_credit_cards=str(row.get('attr_BusinessAcceptsCreditCards')) if pd.notna(row.get('attr_BusinessAcceptsCreditCards')) else None,
                attr_bike_parking=str(row.get('attr_BikeParking')) if pd.notna(row.get('attr_BikeParking')) else None,
                attr_take_out=str(row.get('attr_RestaurantsTakeOut')) if pd.notna(row.get('attr_RestaurantsTakeOut')) else None,
                attr_delivery=str(row.get('attr_RestaurantsDelivery')) if pd.notna(row.get('attr_RestaurantsDelivery')) else None,
                attr_good_for_kids=str(row.get('attr_GoodForKids')) if pd.notna(row.get('attr_GoodForKids')) else None,
                attr_outdoor_seating=str(row.get('attr_OutdoorSeating')) if pd.notna(row.get('attr_OutdoorSeating')) else None,
                attr_has_tv=str(row.get('attr_HasTV')) if pd.notna(row.get('attr_HasTV')) else None,
                attr_reservations=str(row.get('attr_RestaurantsReservations')) if pd.notna(row.get('attr_RestaurantsReservations')) else None,
                attr_caters=str(row.get('attr_Caters')) if pd.notna(row.get('attr_Caters')) else None,
                attr_good_for_groups=str(row.get('attr_RestaurantsGoodForGroups')) if pd.notna(row.get('attr_RestaurantsGoodForGroups')) else None,
                attr_wheelchair=str(row.get('attr_WheelchairAccessible')) if pd.notna(row.get('attr_WheelchairAccessible')) else None,
                attr_dogs_allowed=str(row.get('attr_DogsAllowed')) if pd.notna(row.get('attr_DogsAllowed')) else None,
                attr_table_service=str(row.get('attr_RestaurantsTableService')) if pd.notna(row.get('attr_RestaurantsTableService')) else None,
                attr_happy_hour=str(row.get('attr_HappyHour')) if pd.notna(row.get('attr_HappyHour')) else None,
                attr_by_appointment=str(row.get('attr_ByAppointmentOnly')) if pd.notna(row.get('attr_ByAppointmentOnly')) else None,
                attr_wifi=str(row.get('attr_WiFi')) if pd.notna(row.get('attr_WiFi')) else None,
                attr_alcohol=str(row.get('attr_Alcohol')) if pd.notna(row.get('attr_Alcohol')) else None,
                attr_noise_level=str(row.get('attr_NoiseLevel')) if pd.notna(row.get('attr_NoiseLevel')) else None,
                attr_attire=str(row.get('attr_RestaurantsAttire')) if pd.notna(row.get('attr_RestaurantsAttire')) else None,
                attr_price_range=str(row.get('attr_RestaurantsPriceRange2')) if pd.notna(row.get('attr_RestaurantsPriceRange2')) else None
            )
            db.session.add(biz)
            if _ % 5000 == 0:
                db.session.commit()
                print(f'  已导入 {_+1}/{len(df)}')
        except Exception as e:
            print(f'  错误: {e}')
            continue
    db.session.commit()
    print(f'  商户导入完成: {len(df)} 条')


def import_classification():
    print('导入商户分类...')
    filepath = os.path.join(PROCESSED_DIR, 'business_classification.csv')
    df = pd.read_csv(filepath)
    for _, row in df.iterrows():
        try:
            biz_type = row.get('business_type', '其他')
            if pd.isna(biz_type) or not biz_type:
                biz_type = '其他'
            cls = BusinessClassification(business_id=row.get('business_id'), business_type=str(biz_type))
            db.session.add(cls)
        except:
            continue
    db.session.commit()
    print(f'  分类导入完成: {len(df)} 条')


def import_users():
    print('导入用户数据...')
    filepath = os.path.join(PROCESSED_DIR, 'processed_user.csv')
    df = pd.read_csv(filepath)
    for idx, row in df.iterrows():
        try:
            user = AppUser(
                user_id=row.get('user_id'),
                name=row.get('name') if pd.notna(row.get('name')) else '',
                review_count=int(row.get('review_count', 0)) if pd.notna(row.get('review_count')) else 0,
                review_count_log=row.get('review_count_log') if pd.notna(row.get('review_count_log')) else None,
                yelping_since=pd.to_datetime(row.get('yelping_since')).to_pydatetime() if pd.notna(row.get('yelping_since')) else None,
                useful=int(row.get('useful', 0)) if pd.notna(row.get('useful')) else 0,
                funny=int(row.get('funny', 0)) if pd.notna(row.get('funny')) else 0,
                cool=int(row.get('cool', 0)) if pd.notna(row.get('cool')) else 0,
                fans=int(row.get('fans', 0)) if pd.notna(row.get('fans')) else 0,
                average_stars=row.get('average_stars') if pd.notna(row.get('average_stars')) else 0,
                password_hash=hashlib.sha256('123456'.encode()).hexdigest(),
                role='user'
            )
            db.session.add(user)
            if idx % 5000 == 0:
                db.session.commit()
        except:
            continue
    db.session.commit()

    admin = AppUser(user_id='admin', name='超级管理员', password_hash=hashlib.sha256('admin123'.encode()).hexdigest(), role='admin', review_count=0, useful=0, funny=0, cool=0, fans=0)
    demo = AppUser(user_id='demo', name='演示用户', password_hash=hashlib.sha256('demo123'.encode()).hexdigest(), role='user', review_count=0, useful=0, funny=0, cool=0, fans=0)
    db.session.add(admin)
    db.session.add(demo)
    db.session.commit()
    print(f'  用户导入完成: {len(df)} 条')


def import_reviews():
    print('导入评论数据（分批处理）...')
    filepath = os.path.join(PROCESSED_DIR, 'processed_review.csv')
    chunksize = 50000
    total = 0
    for chunk in pd.read_csv(filepath, chunksize=chunksize):
        for _, row in chunk.iterrows():
            try:
                r = Review(
                    review_id=row.get('review_id'),
                    user_id=row.get('user_id'),
                    business_id=row.get('business_id'),
                    stars=row.get('stars') if pd.notna(row.get('stars')) else None,
                    stars_normalized=row.get('stars_normalized') if pd.notna(row.get('stars_normalized')) else None,
                    useful=int(row.get('useful', 0)) if pd.notna(row.get('useful')) else 0,
                    funny=int(row.get('funny', 0)) if pd.notna(row.get('funny')) else 0,
                    cool=int(row.get('cool', 0)) if pd.notna(row.get('cool')) else 0,
                    year=int(row.get('year', 0)) if pd.notna(row.get('year')) else None,
                    month=int(row.get('month', 0)) if pd.notna(row.get('month')) else None,
                    day=int(row.get('day', 0)) if pd.notna(row.get('day')) else None,
                    text=row.get('text') if pd.notna(row.get('text')) else '',
                    text_cleaned=row.get('text_cleaned') if pd.notna(row.get('text_cleaned')) else ''
                )
                db.session.add(r)
            except:
                continue
        db.session.commit()
        total += len(chunk)
        print(f'  已导入 {total} 条...')
    print(f'  评论导入完成: {total} 条')


def import_tips():
    print('导入提示数据...')
    filepath = os.path.join(PROCESSED_DIR, 'processed_tip.csv')
    df = pd.read_csv(filepath)
    for _, row in df.iterrows():
        try:
            tip = Tip(
                user_id=row.get('user_id'),
                business_id=row.get('business_id'),
                text=row.get('text') if pd.notna(row.get('text')) else '',
                text_cleaned=row.get('text_cleaned') if pd.notna(row.get('text_cleaned')) else '',
                year=int(row.get('year', 0)) if pd.notna(row.get('year')) else None,
                month=int(row.get('month', 0)) if pd.notna(row.get('month')) else None,
                compliment_count=int(row.get('compliment_count', 0)) if pd.notna(row.get('compliment_count')) else 0
            )
            db.session.add(tip)
        except:
            continue
    db.session.commit()
    print(f'  提示导入完成: {len(df)} 条')


def import_checkins():
    print('导入打卡数据...')
    filepath = os.path.join(PROCESSED_DIR, 'processed_checkin.csv')
    df = pd.read_csv(filepath)
    for _, row in df.iterrows():
        try:
            checkin = Checkin(business_id=row.get('business_id'), date=str(row.get('date')) if pd.notna(row.get('date')) else '')
            db.session.add(checkin)
        except:
            continue
    db.session.commit()
    print(f'  打卡导入完成: {len(df)} 条')


def main():
    with app.app_context():
        print('正在删除旧表...')
        db.drop_all()
        print('正在创建新表...')
        db.create_all()

        import_business()
        import_classification()
        import_users()
        import_reviews()
        import_tips()
        import_checkins()

        print(f'\n数据库初始化完成！')
        print(f'  商户: {Business.query.count()}')
        print(f'  用户: {AppUser.query.count()}')
        print(f'  评论: {Review.query.count()}')
        print(f'  提示: {Tip.query.count()}')
        print(f'  打卡: {Checkin.query.count()}')


if __name__ == '__main__':
    main()