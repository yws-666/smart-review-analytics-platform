from app.models import db


class Business(db.Model):
    __tablename__ = 'business'

    business_id = db.Column(db.String(22), primary_key=True)
    name = db.Column(db.String(200))
    address = db.Column(db.String(300))
    city = db.Column(db.String(100), index=True)
    state = db.Column(db.String(10))
    postal_code = db.Column(db.String(20))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    stars = db.Column(db.Float, index=True)
    stars_normalized = db.Column(db.Float)
    review_count = db.Column(db.Integer)
    review_count_log = db.Column(db.Float)
    is_open = db.Column(db.Integer)
    categories = db.Column(db.Text)

    attr_accepts_credit_cards = db.Column(db.String(20))
    attr_bike_parking = db.Column(db.String(20))
    attr_take_out = db.Column(db.String(20))
    attr_delivery = db.Column(db.String(20))
    attr_good_for_kids = db.Column(db.String(20))
    attr_outdoor_seating = db.Column(db.String(20))
    attr_has_tv = db.Column(db.String(20))
    attr_reservations = db.Column(db.String(20))
    attr_caters = db.Column(db.String(20))
    attr_good_for_groups = db.Column(db.String(20))
    attr_wheelchair = db.Column(db.String(20))
    attr_dogs_allowed = db.Column(db.String(20))
    attr_table_service = db.Column(db.String(20))
    attr_happy_hour = db.Column(db.String(20))
    attr_by_appointment = db.Column(db.String(20))
    attr_wifi = db.Column(db.String(20))
    attr_alcohol = db.Column(db.String(20))
    attr_noise_level = db.Column(db.String(20))
    attr_attire = db.Column(db.String(20))
    attr_price_range = db.Column(db.String(20))

    classification = db.relationship('BusinessClassification', backref='business', uselist=False)


class BusinessClassification(db.Model):
    __tablename__ = 'business_classification'

    business_id = db.Column(db.String(22), db.ForeignKey('business.business_id'), primary_key=True)
    business_type = db.Column(db.String(20), index=True)