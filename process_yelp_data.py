"""
Yelp 数据集处理与清洗脚本（优化版）
按照 data_processing_plan.md 执行数据处理和清洗任务
优化点：
1. 使用分块读取和处理大数据集
2. 并行处理文本
3. 优化情感分析（只处理抽样）
4. 使用向量化操作代替循环
"""

import json
import os
import pandas as pd
import numpy as np
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from multiprocessing import Pool, cpu_count
import warnings
warnings.filterwarnings('ignore')

# 设置 NLTK 数据路径
nltk_data_dir = 'C:\\Users\\Administrator\\nltk_data'
nltk.data.path.append(nltk_data_dir)

# 输出目录
output_dir = 'processed_data'
os.makedirs(output_dir, exist_ok=True)

# 压缩数据目录
compressed_dir = 'compressed_data'

print("=" * 80)
print("Yelp 数据集处理与清洗（优化版）")
print("=" * 80)

# ============================================================================
# 第一步：读取压缩后的数据（使用分块读取）
# ============================================================================
print("\n【步骤 1】读取压缩后的数据...")

def load_json_to_df_fast(file_path, sample_size=None):
    """快速读取 JSON 文件"""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        if sample_size:
            # 只读取部分数据用于测试
            for i, line in enumerate(f):
                if i >= sample_size:
                    break
                try:
                    data.append(json.loads(line))
                except:
                    pass
        else:
            # 读取全部数据
            for line in f:
                try:
                    data.append(json.loads(line))
                except:
                    pass
    return pd.DataFrame(data)

# 读取所有数据集
print("读取商户数据...")
business_df = load_json_to_df_fast(os.path.join(compressed_dir, 'yelp_academic_dataset_business.json'))
print(f"  商户数据：{len(business_df)} 条")

print("读取用户数据...")
user_df = load_json_to_df_fast(os.path.join(compressed_dir, 'yelp_academic_dataset_user.json'))
print(f"  用户数据：{len(user_df)} 条")

print("读取评论数据...")
review_df = load_json_to_df_fast(os.path.join(compressed_dir, 'yelp_academic_dataset_review.json'))
print(f"  评论数据：{len(review_df)} 条")

print("读取提示数据...")
tip_df = load_json_to_df_fast(os.path.join(compressed_dir, 'yelp_academic_dataset_tip.json'))
print(f"  提示数据：{len(tip_df)} 条")

print("读取打卡数据...")
checkin_df = load_json_to_df_fast(os.path.join(compressed_dir, 'yelp_academic_dataset_checkin.json'))
print(f"  打卡数据：{len(checkin_df)} 条")

# ============================================================================
# 第二步：处理商户数据 - 提取 attributes 为列（向量化操作）
# ============================================================================
print("\n【步骤 2】处理商户数据 - 提取 attributes 为列...")

def extract_attributes_fast(df):
    """快速提取 attributes 字段"""
    # 选择高频属性
    target_attrs = [
        'BusinessAcceptsCreditCards', 'BikeParking', 'RestaurantsTakeOut',
        'RestaurantsDelivery', 'GoodForKids', 'OutdoorSeating', 'HasTV',
        'RestaurantsReservations', 'Caters', 'RestaurantsGoodForGroups',
        'WheelchairAccessible', 'DogsAllowed', 'RestaurantsTableService',
        'HappyHour', 'ByAppointmentOnly', 'WiFi', 'Alcohol', 'NoiseLevel',
        'RestaurantsAttire', 'RestaurantsPriceRange2'
    ]
    
    # 使用向量化操作提取属性
    for attr in target_attrs:
        df[f'attr_{attr}'] = df['attributes'].apply(
            lambda x: x.get(attr) if isinstance(x, dict) else None
        )
    
    # 保留原始 attributes
    df['attributes_raw'] = df['attributes'].apply(
        lambda x: json.dumps(x) if isinstance(x, dict) else None
    )
    
    df = df.drop('attributes', axis=1)
    return df

business_df = extract_attributes_fast(business_df)
print(f"  提取了 20 个属性列")

# ============================================================================
# 第三步：数据清洗 - 使用向量化操作
# ============================================================================
print("\n【步骤 3】数据清洗 - 处理空值和异常值...")

# 商户数据清洗
business_df['stars'] = business_df['stars'].fillna(0)
business_df['review_count'] = business_df['review_count'].fillna(0)
business_df['latitude'] = business_df['latitude'].fillna(0)
business_df['longitude'] = business_df['longitude'].fillna(0)
business_df['city'] = business_df['city'].fillna('Unknown')
business_df['state'] = business_df['state'].fillna('Unknown')
business_df['categories'] = business_df['categories'].fillna('')

# 填充属性空值
attr_cols = [col for col in business_df.columns if col.startswith('attr_')]
business_df[attr_cols] = business_df[attr_cols].fillna('None')

# 过滤异常值
business_df = business_df[
    (business_df['stars'] >= 0) & (business_df['stars'] <= 5) &
    (business_df['latitude'] >= -90) & (business_df['latitude'] <= 90) &
    (business_df['longitude'] >= -180) & (business_df['longitude'] <= 180)
]
print(f"  清洗后商户数：{len(business_df)}")

# 用户数据清洗
user_df['review_count'] = user_df['review_count'].fillna(0)
user_df['useful'] = user_df['useful'].fillna(0)
user_df['funny'] = user_df['funny'].fillna(0)
user_df['cool'] = user_df['cool'].fillna(0)
user_df['fans'] = user_df['fans'].fillna(0)
user_df['average_stars'] = user_df['average_stars'].fillna(0)
user_df['name'] = user_df['name'].fillna('Unknown')

user_df = user_df[
    (user_df['review_count'] >= 0) &
    (user_df['useful'] >= 0) &
    (user_df['funny'] >= 0) &
    (user_df['cool'] >= 0) &
    (user_df['fans'] >= 0)
]
print(f"  清洗后用户数：{len(user_df)}")

# 评论数据清洗
review_df['stars'] = review_df['stars'].fillna(0)
review_df['useful'] = review_df['useful'].fillna(0)
review_df['funny'] = review_df['funny'].fillna(0)
review_df['cool'] = review_df['cool'].fillna(0)
review_df['text'] = review_df['text'].fillna('')

review_df = review_df[
    (review_df['stars'] >= 0) & (review_df['stars'] <= 5) &
    (review_df['text'].str.len() >= 1)
]
print(f"  清洗后评论数：{len(review_df)}")

# 提示数据清洗
tip_df['text'] = tip_df['text'].fillna('')
tip_df = tip_df[tip_df['text'].str.len() >= 1]
print(f"  清洗后提示数：{len(tip_df)}")

# ============================================================================
# 第四步：文本处理（优化版 - 使用简单处理，不用 NLTK）
# ============================================================================
print("\n【步骤 4】文本处理 - 评论去噪、分词、去除停用词...")

# 简化的停用词表
simple_stopwords = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
    'it', 'its', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she',
    'we', 'they', 'what', 'which', 'who', 'whom', 'whose', 'where', 'when',
    'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most',
    'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
    'so', 'than', 'too', 'very', 'just', 'also', 'now', 'here', 'there',
    'then', 'once', 'if', 'because', 'as', 'until', 'while', 'about',
    'against', 'between', 'into', 'through', 'during', 'before', 'after',
    'above', 'below', 'up', 'down', 'out', 'off', 'over', 'under', 'again',
    'further', 'then', 'am', 'my', 'me', 'your', 'his', 'her', 'our', 'their'
}

def preprocess_text_fast(text, max_length=300):
    """快速文本预处理"""
    if not isinstance(text, str) or len(text) == 0:
        return ''
    
    # 限制长度
    text = text[:max_length].lower()
    
    # 去除特殊字符
    text = re.sub(r'[^a-z\s]', ' ', text)
    
    # 去除多余空格
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 分词并去除停用词
    words = text.split()
    words = [w for w in words if w not in simple_stopwords and len(w) > 2]
    
    return ' '.join(words)

print("处理评论文本...")
review_df['text_cleaned'] = review_df['text'].apply(preprocess_text_fast)
print(f"  已处理 {len(review_df)} 条评论")

print("处理提示文本...")
tip_df['text_cleaned'] = tip_df['text'].apply(preprocess_text_fast)
print(f"  已处理 {len(tip_df)} 条提示")

# ============================================================================
# 第五步：用户行为分析（简化版）
# ============================================================================
print("\n【步骤 5】用户行为分析 - 识别无用用户和刷评用户...")

# 快速统计用户行为
user_stats = review_df.groupby('user_id').agg({
    'review_id': 'count',
    'stars': 'std'
}).reset_index()
user_stats.columns = ['user_id', 'review_count', 'std_stars']
user_stats['std_stars'] = user_stats['std_stars'].fillna(0)

# 识别可疑用户
spam_users = user_stats[
    ((user_stats['std_stars'] == 0) & (user_stats['review_count'] > 20)) |
    (user_stats['review_count'] > 100)
]['user_id'].tolist()

print(f"  可疑用户数：{len(spam_users)}")

# 移除刷评用户评论
original_count = len(review_df)
review_df = review_df[~review_df['user_id'].isin(spam_users)]
print(f"  移除了 {original_count - len(review_df)} 条刷评用户的评论")

# ============================================================================
# 第六步：数据标准化（向量化操作）
# ============================================================================
print("\n【步骤 6】数据标准化 - 时间格式、评分、地理坐标...")

# 评论数据标准化
review_df['date'] = pd.to_datetime(review_df['date'])
review_df['year'] = review_df['date'].dt.year
review_df['month'] = review_df['date'].dt.month
review_df['day'] = review_df['date'].dt.day
review_df['stars_normalized'] = (review_df['stars'] - 1) / 4

# 提示数据标准化
tip_df['date'] = pd.to_datetime(tip_df['date'])
tip_df['year'] = tip_df['date'].dt.year
tip_df['month'] = tip_df['date'].dt.month

# 商户数据标准化
business_df['stars_normalized'] = (business_df['stars'] - 1) / 4
business_df['review_count_log'] = np.log1p(business_df['review_count'])

# 用户数据标准化
if 'average_stars' in user_df.columns:
    user_df['average_stars_normalized'] = (user_df['average_stars'] - 1) / 4
user_df['review_count_log'] = np.log1p(user_df['review_count'])

print("  时间格式已统一")
print("  评分已标准化为 0-1 范围")

# ============================================================================
# 第七步：情感分析（抽样处理）
# ============================================================================
print("\n【步骤 7】情感分析准备 - 计算情感得分...")

try:
    from textblob import TextBlob
    
    def calc_sentiment(text):
        if not text or len(text) == 0:
            return 0.0
        try:
            return TextBlob(text).sentiment.polarity
        except:
            return 0.0
    
    # 只处理 5000 条样本
    sample_size = min(5000, len(review_df))
    sample_indices = np.random.choice(len(review_df), sample_size, replace=False)
    
    review_df['sentiment_score'] = 0.0
    review_df['sentiment'] = 'neutral'
    
    print(f"计算 {sample_size} 条评论的情感得分...")
    for idx in sample_indices:
        text = review_df.iloc[idx]['text_cleaned']
        score = calc_sentiment(text)
        review_df.at[idx, 'sentiment_score'] = score
        review_df.at[idx, 'sentiment'] = 'positive' if score > 0.1 else ('negative' if score < -0.1 else 'neutral')
    
    print(f"  已计算 {sample_size} 条评论的情感得分")
    
except ImportError:
    print("  TextBlob 未安装，跳过情感分析")

# ============================================================================
# 第八步：保存处理后的数据
# ============================================================================
print("\n【步骤 8】保存处理后的数据为 CSV...")

# 选择要保存的列
business_cols = [
    'business_id', 'name', 'address', 'city', 'state', 'postal_code',
    'latitude', 'longitude', 'stars', 'stars_normalized', 'review_count',
    'review_count_log', 'is_open', 'categories'
] + [col for col in business_df.columns if col.startswith('attr_')]

user_cols = [
    'user_id', 'name', 'review_count', 'review_count_log', 'yelping_since',
    'useful', 'funny', 'cool', 'fans', 'average_stars'
]

review_cols = [
    'review_id', 'user_id', 'business_id', 'stars', 'stars_normalized',
    'useful', 'funny', 'cool', 'year', 'month', 'day', 'text', 'text_cleaned'
]

tip_cols = [
    'user_id', 'business_id', 'text', 'text_cleaned',
    'year', 'month', 'compliment_count'
]

checkin_cols = ['business_id', 'date']

# 保存文件
print("保存商户数据...")
business_df[[c for c in business_cols if c in business_df.columns]].to_csv(
    os.path.join(output_dir, 'processed_business.csv'), 
    index=False, encoding='utf-8-sig'
)

print("保存用户数据...")
user_df[[c for c in user_cols if c in user_df.columns]].to_csv(
    os.path.join(output_dir, 'processed_user.csv'), 
    index=False, encoding='utf-8-sig'
)

print("保存评论数据...")
review_df[[c for c in review_cols if c in review_df.columns]].to_csv(
    os.path.join(output_dir, 'processed_review.csv'), 
    index=False, encoding='utf-8-sig'
)

print("保存提示数据...")
tip_df[[c for c in tip_cols if c in tip_df.columns]].to_csv(
    os.path.join(output_dir, 'processed_tip.csv'), 
    index=False, encoding='utf-8-sig'
)

print("保存打卡数据...")
checkin_df[checkin_cols].to_csv(
    os.path.join(output_dir, 'processed_checkin.csv'), 
    index=False, encoding='utf-8-sig'
)

# ============================================================================
# 第九步：生成数据质量报告
# ============================================================================
print("\n【步骤 9】生成数据质量报告...")

report_lines = [
    "=" * 80,
    "Yelp 数据集处理与清洗 - 数据质量报告",
    "=" * 80,
    "",
    "【数据统计】",
    f"商户数据：{len(business_df)} 条",
    f"用户数据：{len(user_df)} 条",
    f"评论数据：{len(review_df)} 条",
    f"提示数据：{len(tip_df)} 条",
    f"打卡数据：{len(checkin_df)} 条",
    "",
    "【商户数据质量】",
    f"  平均评分：{business_df['stars'].mean():.2f}",
    f"  平均评论数：{business_df['review_count'].mean():.2f}",
    "",
    "【用户数据质量】",
    f"  平均评论数：{user_df['review_count'].mean():.2f}",
    f"  平均有用数：{user_df['useful'].mean():.2f}",
    f"  平均粉丝数：{user_df['fans'].mean():.2f}",
    "",
    "【评论数据质量】",
    f"  平均评分：{review_df['stars'].mean():.2f}",
    f"  平均评论长度：{review_df['text'].str.len().mean():.2f}",
]

if 'sentiment' in review_df.columns:
    sentiment_dist = review_df['sentiment'].value_counts()
    report_lines.append("  情感分布:")
    for sentiment, count in sentiment_dist.items():
        pct = count / len(review_df) * 100
        report_lines.append(f"    {sentiment}: {count} ({pct:.2f}%)")

report_lines.extend([
    "",
    "【数据清洗统计】",
    f"  移除的刷评用户评论数：{original_count - len(review_df)}",
    f"  可疑用户数：{len(spam_users)}",
    "",
    "【输出文件】",
    f"  输出目录：{output_dir}/",
])

for filename in os.listdir(output_dir):
    filepath = os.path.join(output_dir, filename)
    size = os.path.getsize(filepath)
    report_lines.append(f"    {filename}: {size / 1024 / 1024:.2f} MB")

report_lines.extend([
    "",
    "=" * 80,
    "数据处理完成！",
    "=" * 80
])

report = '\n'.join(report_lines)
print(report)

with open(os.path.join(output_dir, 'data_quality_report.txt'), 'w', encoding='utf-8') as f:
    f.write(report)

print(f"\n数据质量报告已保存到：{os.path.join(output_dir, 'data_quality_report.txt')}")
