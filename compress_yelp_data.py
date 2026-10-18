import json
import os
from collections import defaultdict

# 文件路径
business_file = 'yelp_academic_dataset_business.json'
checkin_file = 'yelp_academic_dataset_checkin.json'
review_file = 'yelp_academic_dataset_review.json'
tip_file = 'yelp_academic_dataset_tip.json'
user_file = 'yelp_academic_dataset_user.json'

# 输出文件路径
output_dir = 'compressed_data'
os.makedirs(output_dir, exist_ok=True)

output_business = os.path.join(output_dir, 'yelp_academic_dataset_business.json')
output_checkin = os.path.join(output_dir, 'yelp_academic_dataset_checkin.json')
output_review = os.path.join(output_dir, 'yelp_academic_dataset_review.json')
output_tip = os.path.join(output_dir, 'yelp_academic_dataset_tip.json')
output_user = os.path.join(output_dir, 'yelp_academic_dataset_user.json')
output_stats = os.path.join(output_dir, 'data_stats.json')

def main():
    print("开始处理Yelp数据集...")
    
    # 1. 筛选活跃商户
    print("步骤1: 筛选活跃商户...")
    active_business_ids = set()
    business_count = 0
    active_business_count = 0
    
    with open(business_file, 'r', encoding='utf-8') as f:
        for line in f:
            business_count += 1
            try:
                business = json.loads(line)
                if business.get('is_open') == 1:
                    active_business_ids.add(business['business_id'])
                    active_business_count += 1
            except json.JSONDecodeError:
                pass
    
    print(f"总商户数: {business_count}")
    print(f"活跃商户数: {active_business_count}")
    
    # 2. 处理评论和提示，收集用户ID并统计评论数
    print("步骤2: 处理评论和提示...")
    user_review_count = defaultdict(int)
    relevant_reviews = []
    relevant_tips = []
    
    # 处理评论
    review_count = 0
    relevant_review_count = 0
    with open(review_file, 'r', encoding='utf-8') as f:
        for line in f:
            review_count += 1
            try:
                review = json.loads(line)
                if review['business_id'] in active_business_ids:
                    relevant_reviews.append(review)
                    user_review_count[review['user_id']] += 1
                    relevant_review_count += 1
            except json.JSONDecodeError:
                pass
    
    # 处理提示
    tip_count = 0
    relevant_tip_count = 0
    with open(tip_file, 'r', encoding='utf-8') as f:
        for line in f:
            tip_count += 1
            try:
                tip = json.loads(line)
                if tip['business_id'] in active_business_ids:
                    relevant_tips.append(tip)
                    user_review_count[tip['user_id']] += 1
                    relevant_tip_count += 1
            except json.JSONDecodeError:
                pass
    
    print(f"总评论数: {review_count}")
    print(f"相关评论数: {relevant_review_count}")
    print(f"总提示数: {tip_count}")
    print(f"相关提示数: {relevant_tip_count}")
    
    # 3. 筛选活跃用户（至少10条评论）
    print("步骤3: 筛选活跃用户...")
    active_user_ids = set()
    for user_id, count in user_review_count.items():
        if count >= 10:
            active_user_ids.add(user_id)
    
    print(f"活跃用户数: {len(active_user_ids)}")
    
    # 4. 进一步筛选，只保留活跃用户的评论和提示
    print("步骤4: 进一步筛选评论和提示...")
    final_reviews = []
    final_tips = []
    
    for review in relevant_reviews:
        if review['user_id'] in active_user_ids:
            final_reviews.append(review)
    
    for tip in relevant_tips:
        if tip['user_id'] in active_user_ids:
            final_tips.append(tip)
    
    print(f"最终评论数: {len(final_reviews)}")
    print(f"最终提示数: {len(final_tips)}")
    
    # 5. 处理打卡数据
    print("步骤5: 处理打卡数据...")
    relevant_checkins = []
    checkin_count = 0
    relevant_checkin_count = 0
    
    with open(checkin_file, 'r', encoding='utf-8') as f:
        for line in f:
            checkin_count += 1
            try:
                checkin = json.loads(line)
                if checkin['business_id'] in active_business_ids:
                    relevant_checkins.append(checkin)
                    relevant_checkin_count += 1
            except json.JSONDecodeError:
                pass
    
    print(f"总打卡数: {checkin_count}")
    print(f"相关打卡数: {relevant_checkin_count}")
    
    # 6. 处理用户数据
    print("步骤6: 处理用户数据...")
    relevant_users = []
    user_count = 0
    relevant_user_count = 0
    
    with open(user_file, 'r', encoding='utf-8') as f:
        for line in f:
            user_count += 1
            try:
                user = json.loads(line)
                if user['user_id'] in active_user_ids:
                    relevant_users.append(user)
                    relevant_user_count += 1
            except json.JSONDecodeError:
                pass
    
    print(f"总用户数: {user_count}")
    print(f"相关用户数: {relevant_user_count}")
    
    # 7. 处理商户数据，确保每个商户都有互动数据
    print("步骤7: 处理商户数据...")
    # 收集有互动的商户ID
    businesses_with_interaction = set()
    for review in final_reviews:
        businesses_with_interaction.add(review['business_id'])
    for tip in final_tips:
        businesses_with_interaction.add(tip['business_id'])
    for checkin in relevant_checkins:
        businesses_with_interaction.add(checkin['business_id'])
    
    # 筛选商户
    final_businesses = []
    with open(business_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                business = json.loads(line)
                if business['business_id'] in businesses_with_interaction and business.get('is_open') == 1:
                    final_businesses.append(business)
            except json.JSONDecodeError:
                pass
    
    print(f"最终商户数: {len(final_businesses)}")
    
    # 8. 写入输出文件
    print("步骤8: 写入输出文件...")
    
    # 写入商户数据
    with open(output_business, 'w', encoding='utf-8') as f:
        for business in final_businesses:
            f.write(json.dumps(business) + '\n')
    
    # 写入打卡数据
    with open(output_checkin, 'w', encoding='utf-8') as f:
        for checkin in relevant_checkins:
            if checkin['business_id'] in businesses_with_interaction:
                f.write(json.dumps(checkin) + '\n')
    
    # 写入评论数据
    with open(output_review, 'w', encoding='utf-8') as f:
        for review in final_reviews:
            f.write(json.dumps(review) + '\n')
    
    # 写入提示数据
    with open(output_tip, 'w', encoding='utf-8') as f:
        for tip in final_tips:
            f.write(json.dumps(tip) + '\n')
    
    # 写入用户数据
    with open(output_user, 'w', encoding='utf-8') as f:
        for user in relevant_users:
            f.write(json.dumps(user) + '\n')
    
    # 9. 生成统计报告
    print("步骤9: 生成统计报告...")
    stats = {
        'original': {
            'businesses': business_count,
            'reviews': review_count,
            'tips': tip_count,
            'checkins': checkin_count,
            'users': user_count
        },
        'compressed': {
            'businesses': len(final_businesses),
            'reviews': len(final_reviews),
            'tips': len(final_tips),
            'checkins': len([c for c in relevant_checkins if c['business_id'] in businesses_with_interaction]),
            'users': len(relevant_users)
        },
        'compression_ratio': {
            'businesses': len(final_businesses) / business_count if business_count > 0 else 0,
            'reviews': len(final_reviews) / review_count if review_count > 0 else 0,
            'tips': len(final_tips) / tip_count if tip_count > 0 else 0,
            'checkins': len([c for c in relevant_checkins if c['business_id'] in businesses_with_interaction]) / checkin_count if checkin_count > 0 else 0,
            'users': len(relevant_users) / user_count if user_count > 0 else 0
        }
    }
    
    with open(output_stats, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print("数据处理完成！")
    print(f"输出目录: {output_dir}")
    print(f"统计报告: {output_stats}")

if __name__ == "__main__":
    main()
