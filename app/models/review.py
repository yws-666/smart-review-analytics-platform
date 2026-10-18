from app.models import db
from app.models.business import Business


class Review(db.Model):
    __tablename__ = 'review'

    review_id = db.Column(db.String(22), primary_key=True)
    user_id = db.Column(db.String(22), db.ForeignKey('app_user.user_id'), index=True)
    business_id = db.Column(db.String(22), db.ForeignKey('business.business_id'), index=True)
    stars = db.Column(db.Float, index=True)
    stars_normalized = db.Column(db.Float)
    useful = db.Column(db.Integer)
    funny = db.Column(db.Integer)
    cool = db.Column(db.Integer)
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    day = db.Column(db.Integer)
    text = db.Column(db.Text)
    text_cleaned = db.Column(db.Text)


class Tip(db.Model):
    __tablename__ = 'tip'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(22), db.ForeignKey('app_user.user_id'))
    business_id = db.Column(db.String(22), db.ForeignKey('business.business_id'), index=True)
    text = db.Column(db.Text)
    text_cleaned = db.Column(db.Text)
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    compliment_count = db.Column(db.Integer)


class Checkin(db.Model):
    __tablename__ = 'checkin'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    business_id = db.Column(db.String(22), db.ForeignKey('business.business_id'), index=True)
    date = db.Column(db.Text)


class UserFavorite(db.Model):
    __tablename__ = 'user_favorite'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(22), db.ForeignKey('app_user.user_id'), index=True)
    business_id = db.Column(db.String(22), db.ForeignKey('business.business_id'))
    created_at = db.Column(db.DateTime)
    
    business = db.relationship('Business', backref='favorites')


class BrowseHistory(db.Model):
    __tablename__ = 'browse_history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(22), db.ForeignKey('app_user.user_id'), index=True)
    business_id = db.Column(db.String(22), db.ForeignKey('business.business_id'))
    browsed_at = db.Column(db.DateTime)
    
    business = db.relationship('Business', backref='history')


class ReviewVote(db.Model):
    __tablename__ = 'review_vote'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(22), db.ForeignKey('app_user.user_id'), index=True)
    review_id = db.Column(db.String(22), db.ForeignKey('review.review_id'), index=True)
    vote_type = db.Column(db.String(20))
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'review_id', 'vote_type', name='_user_review_vote_unique'),
    )