from website import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Images(db.Model):
    img_id = db.Column(db.Integer, primary_key=True)
    img_person = db.Column(db.String(3))

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(255))
    address = db.Column(db.String(50))
    is_verif = db.Column(db.Integer)
    is_admin = db.Column(db.Integer)

class Attendance(db.Model):
    accs_id = db.Column(db.Integer, nullable=False, primary_key=True)
    accs_date = db.Column(db.Date, nullable=False)
    accs_prsn = db.Column(db.String(3), nullable=False)
    accs_added = db.Column(db.DateTime, nullable=False)
    

class Events(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    img_events = db.Column(db.String(255))
    date_events = db.Column(db.Date)
    venue = db.Column(db.String(50))


class Booking(db.Model):
    __tablename__ = "booking"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    events_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    book_date = db.Column(db.Date(), default=func.now())
