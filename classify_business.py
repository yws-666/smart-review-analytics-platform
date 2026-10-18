"""
商户分类脚本
将商户按 categories 归为大类别
"""

import pandas as pd
import json

# 定义大类别及其包含的关键词
CATEGORY_MAPPING = {
    '美食餐饮': [
        'Restaurants', 'Food', 'Sandwiches', 'American (Traditional)', 'Fast Food',
        'Pizza', 'Coffee & Tea', 'Breakfast & Brunch', 'Burgers', 'Mexican',
        'Italian', 'Seafood', 'Chicken Wings', 'Chinese', 'Salad', 'Bakeries',
        'Desserts', 'Sushi Bars', 'Thai', 'Indian', 'Japanese', 'Korean',
        'Vietnamese', 'Mediterranean', 'Greek', 'French', 'Steakhouses',
        'Barbeque', 'Caterers', 'Food Trucks', 'Ice Cream & Frozen Yogurt',
        'Donuts', 'Cupcakes', 'Cafes', 'Bubble Tea', 'Juice Bars & Smoothies',
        'Soup', 'Noodles', 'Ramen', 'Tapas/Small Plates', 'Poke', 'Halal',
        'Kosher', 'Vegan', 'Vegetarian', 'Gluten-Free', 'Comfort Food',
        'Soul Food', 'Southern', 'Tex-Mex', 'Latin American', 'Caribbean',
        'Middle Eastern', 'African', 'Russian', 'German', 'Spanish',
        'Portuguese', 'Brazilian', 'Argentine', 'Peruvian', 'Cuban',
        'Asian Fusion', 'Chinese', 'Japanese', 'Korean', 'Vietnamese',
        'Thai', 'Indian', 'Pakistani', 'Bangladeshi', 'Sri Lankan',
        'Burmese', 'Cambodian', 'Laotian', 'Malaysian', 'Singaporean',
        'Indonesian', 'Filipino', 'Taiwanese', 'Hong Kong Style Cafe',
        'Shanghainese', 'Szechuan', 'Cantonese', 'Dim Sum', 'Hot Pot'
    ],
    '购物零售': [
        'Shopping', 'Fashion', 'Grocery', 'Specialty Food', 'Convenience Stores',
        'Department Stores', 'Electronics', 'Mobile Phones', 'Computers',
        'Appliances', 'Furniture Stores', 'Home Decor', 'Jewelry', 'Watches',
        'Shoes', 'Sports Wear', 'Lingerie', 'Maternity Wear', 'Plus Size Fashion',
        'Children\'s Clothing', 'Men\'s Clothing', 'Women\'s Clothing',
        'Accessories', 'Handbags', 'Luggage', 'Sunglasses', 'Opticians',
        'Cosmetics & Beauty Supply', 'Drugstores', 'Pharmacy', 'Health Markets',
        'Farmers Market', 'Butcher', 'Cheese Shops', 'Wine & Spirits',
        'Beer, Wine & Spirits', 'Tobacco Shops', 'Vape Shops', 'Head Shops',
        'Gift Shops', 'Cards & Stationery', 'Flowers & Gifts', 'Florists',
        'Balloons', 'Personalized Items', 'Customized Merchandise',
        'Art Supplies', 'Craft Supplies', 'Hobby Shops', 'Musical Instruments',
        'Books, Mags, Music & Video', 'Bookstores', 'Comic Books', 'Video Game Stores',
        'Toy Stores', 'Hobby Shops', 'Pet Stores', 'Pet Groomers'
    ],
    '酒店旅游': [
        'Hotels & Travel', 'Hotels', 'Hostels', 'Bed & Breakfast',
        'Resorts', 'Vacation Rentals', 'Tours', 'Travel Services',
        'Travel Agents', 'Airlines', 'Airports', 'Taxis', 'Airport Shuttles',
        'Limos', 'Public Transportation', 'Trains', 'Bus Stations',
        'RV Parks', 'Campgrounds', 'Visitor Centers', 'Landmarks & Historical Buildings',
        'Museums', 'Art Galleries', 'Observatories', 'Planetarium',
        'Botanical Gardens', 'Zoos', 'Aquariums', 'Beaches', 'Parks',
        'Playgrounds', 'Dog Parks', 'Skate Parks', 'Community Centers',
        'Cultural Center', 'Visitor Centers', 'Tourist Information'
    ],
    '休闲娱乐': [
        'Nightlife', 'Bars', 'Arts & Entertainment', 'Active Life',
        'Music Venues', 'Karaoke', 'Comedy Clubs', 'Dance Clubs',
        'Jazz & Blues', 'Piano Bars', 'Sports Bars', 'Wine Bars',
        'Beer Bar', 'Cocktail Bars', 'Hookah Bars', 'Pubs', 'Dive Bars',
        'Lounges', 'Clubs', 'Adult Entertainment', 'Cabaret', 'Casinos',
        'Arcades', 'Bowling', 'Pool Halls', 'Karaoke', 'Cinema',
        'Movie Theaters', 'Drive-In Theater', 'Performing Arts',
        'Theater', 'Opera & Ballet', 'Symphonies', 'Art Galleries',
        'Museums', 'Planetarium', 'Observatories', 'Aquariums', 'Zoos',
        'Botanical Gardens', 'Amusement Parks', 'Theme Parks', 'Water Parks',
        'Go Karts', 'Mini Golf', 'Golf', 'Skiing', 'Skating Rinks',
        'Rock Climbing', 'Trampoline Parks', 'Escape Games', 'Paintball',
        'Laser Tag', 'Virtual Reality Centers', 'Axe Throwing', 'Archery'
    ],
    '生活服务': [
        'Home Services', 'Local Services', 'Professional Services',
        'Home & Garden', 'Real Estate', 'Apartments', 'Property Management',
        'Home Cleaning', 'Office Cleaning', 'Carpet Cleaning', 'Window Washing',
        'Pressure Washers', 'Gutter Services', 'Chimney Sweeps', 'Pest Control',
        'Handyman', 'Electricians', 'Plumbing', 'HVAC', 'Heating & Air Conditioning',
        'Appliances & Repair', 'Home Automation', 'Home Theatre Installation',
        'Security Systems', 'Fire Protection Services', 'Keys & Locksmiths',
        'Safe Stores', 'Self Storage', 'Movers', 'Packing Services',
        'Junk Removal & Hauling', 'Recycling Center', 'Donation Center',
        'Dry Cleaning & Laundry', 'Laundromat', 'Sewing & Alterations',
        'Shoe Repair', 'Watch Repair', 'Jewelry Repair', 'Electronics Repair',
        'Mobile Phone Repair', 'Computer Repair', 'Data Recovery',
        'IT Services & Computer Repair', 'Printing Services', 'Graphic Design',
        'Web Design', 'Marketing', 'Advertising', 'Public Relations',
        'Employment Agencies', 'Career Counseling', 'Business Consulting',
        'Financial Services', 'Accountants', 'Tax Services', 'Insurance',
        'Banks & Credit Unions', 'Mortgage Brokers', 'Financial Advising',
        'Investing', 'Currency Exchange', 'Check Cashing/Pay-day Loans',
        'Title Loans', 'Notaries', 'Translation Services', 'Shredding Services'
    ],
    '医疗健康': [
        'Health & Medical', 'Doctors', 'Dentists', 'Hospitals', 'Urgent Care',
        'Emergency Rooms', 'Medical Centers', 'Physical Therapy', 'Chiropractors',
        'Massage Therapy', 'Acupuncture', 'Traditional Chinese Medicine',
        'Naturopathic/Holistic', 'Homeopathic', 'Hypnosis/Hypnotherapy',
        'Psychologists', 'Psychiatrists', 'Counseling & Mental Health',
        'Addiction Medicine', 'Rehabilitation Center', 'Weight Loss Centers',
        'Nutritionists', 'Dietitians', 'Sports Medicine', 'Orthopedists',
        'Podiatrists', 'Ophthalmologists', 'Optometrists', 'Opticians',
        'Laser Eye Surgery/Lasik', 'Dermatologists', 'Cosmetic Surgeons',
        'Plastic Surgeons', 'Medical Spas', 'Hair Removal', 'Skin Care',
        'Waxing', 'Tattoo Removal', 'Fertility', 'Obstetricians & Gynecologists',
        'Midwives', 'Lactation Services', 'Pediatricians', 'Gerontologists',
        'Allergists', 'Immunodermatologists', 'Cardiologists', 'Endocrinologists',
        'Gastroenterologists', 'Nephrologists', 'Neurologists', 'Oncologists',
        'Pulmonologists', 'Rheumatologists', 'Urologists', 'Vascular Medicine',
        'Laboratory Testing', 'Diagnostic Imaging', 'Radiologists', 'MRI',
        'Pharmacy', 'Drugstores', 'Medical Supplies', 'Mobility Equipment',
        'Prosthetics', 'Hearing Aids', 'Audiologist', 'Speech Therapists',
        'Occupational Therapy', 'Home Health Care', 'Hospice', 'Assisted Living Facilities',
        'Retirement Homes', 'Nursing Homes'
    ],
    '美容美发': [
        'Beauty & Spas', 'Hair Salons', 'Nail Salons', 'Skin Care',
        'Hair Removal', 'Waxing', 'Day Spas', 'Medical Spas',
        'Massage', 'Massage Therapy', 'Tanning', 'Spray Tanning',
        'Tattoo', 'Piercing', 'Cosmetics & Beauty Supply',
        'Makeup Artists', 'Hair Stylists', 'Barbers', 'Eyelash Service',
        'Eyebrow Services', 'Teeth Whitening', 'Float Spa', 'Saunas',
        'Health Retreats', 'Weight Loss Centers', 'Yoga', 'Pilates',
        'Meditation Centers'
    ],
    '汽车服务': [
        'Automotive', 'Auto Repair', 'Tires', 'Oil Change Stations',
        'Auto Detailing', 'Car Wash', 'Car Dealers', 'Auto Parts & Supplies',
        'Auto Glass Services', 'Auto Upholstery', 'Auto Customization',
        'Auto Loan Providers', 'Auto Insurance', 'Motorcycle Dealers',
        'Motorcycle Repair', 'Scooter Rentals', 'Bicycles', 'Bike Rentals',
        'Bike Repair/Maintenance', 'Bike Parking', 'EV Charging Stations',
        'Parking', 'Gas Stations', 'Smog Check Stations', 'Vehicle Inspections',
        'Towing', 'Roadside Assistance', 'Auto Electric Services',
        'Transmission Repair', 'Wheel & Rim Repair', 'Body Shops',
        'Paintless Dent Removal', 'RV Dealers', 'RV Repair', 'RV Rental',
        'Boat Dealers', 'Boat Repair', 'Marinas', 'Boating'
    ],
    '宠物服务': [
        'Pets', 'Pet Services', 'Pet Stores', 'Pet Groomers',
        'Pet Boarding/Pet Sitting', 'Pet Training', 'Veterinarians',
        'Animal Shelters', 'Pet Adoption', 'Pet Photography',
        'Dog Walkers', 'Pet Breeders', 'Pet Cremation Services',
        'Pet Insurance', 'Aquarium Services', 'Horse Boarding',
        'Horseback Riding', 'Stables'
    ],
    '教育培训': [
        'Education', 'Colleges & Universities', 'Vocational & Technical School',
        'Specialty Schools', 'Cooking Classes', 'Art Classes', 'Dance Schools',
        'Music Lessons', 'Language Schools', 'Tutoring Centers', 'Test Preparation',
        'Preschools', 'Elementary Schools', 'Middle Schools & High Schools',
        'Private Schools', 'Religious Schools', 'Montessori Schools',
        'Special Education', 'Adult Education', 'Libraries', 'Museums',
        'Planetarium', 'Observatories', 'Community Centers', 'Kids Activities',
        'Summer Camps', 'After School Programs', 'Child Care & Day Care',
        'Nanny Services', 'Parenting Classes'
    ]
}

def classify_business(categories_str):
    """根据类别字符串分类商户"""
    if not categories_str or pd.isna(categories_str):
        return '其他'
    
    # 分割类别
    cats = [c.strip() for c in categories_str.split(',')]
    
    # 统计每个大类别的匹配数
    category_scores = {}
    for main_cat, keywords in CATEGORY_MAPPING.items():
        score = sum(1 for cat in cats if cat in keywords)
        if score > 0:
            category_scores[main_cat] = score
    
    # 返回匹配数最多的类别，如果没有匹配则返回'其他'
    if category_scores:
        return max(category_scores, key=category_scores.get)
    return '其他'

# 读取商户数据
print("读取商户数据...")
df = pd.read_csv('processed_data/processed_business.csv', usecols=['business_id', 'categories'])
print(f"总商户数：{len(df)}")

# 分类商户
print("\n正在分类商户...")
df['business_type'] = df['categories'].apply(classify_business)

# 统计各类别数量
print("\n商户分类统计：")
type_counts = df['business_type'].value_counts()
for biz_type, count in type_counts.items():
    print(f"  {biz_type}: {count} 家")

# 保存分类结果
output_df = df[['business_id', 'business_type']].copy()
output_df.to_csv('processed_data/business_classification.csv', index=False, encoding='utf-8-sig')

print(f"\n分类结果已保存到：processed_data/business_classification.csv")
print(f"总商户数：{len(output_df)}")
print(f"已分类商户数：{len(output_df[output_df['business_type'] != '其他'])}")
print(f"未分类商户数：{len(output_df[output_df['business_type'] == '其他'])}")

# 验证数据完整性
print("\n数据完整性验证：")
print(f"  所有商户都有类别：{output_df['business_type'].notna().all()}")
print(f"  无空值：{output_df.isnull().sum().sum() == 0}")
print(f"  类别数：{output_df['business_type'].nunique()}")
