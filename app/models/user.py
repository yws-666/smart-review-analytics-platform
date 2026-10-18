from app.models import db


class AppUser(db.Model):
    __tablename__ = 'app_user'

    user_id = db.Column(db.String(22), primary_key=True)
    name = db.Column(db.String(100))
    review_count = db.Column(db.Integer)
    review_count_log = db.Column(db.Float)
    yelping_since = db.Column(db.DateTime)
    useful = db.Column(db.Integer)
    funny = db.Column(db.Integer)
    cool = db.Column(db.Integer)
    fans = db.Column(db.Integer)
    average_stars = db.Column(db.Float)
    password_hash = db.Column(db.String(200))
    role = db.Column(db.String(20), default='user')
    preferences = db.Column(db.Text)

    reviews = db.relationship('Review', backref='user', lazy='dynamic')
    favorites = db.relationship('UserFavorite', backref='user', lazy='dynamic')