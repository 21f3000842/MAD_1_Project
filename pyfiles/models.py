from pyfiles.database import db
from datetime import datetime, timezone

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(200), nullable=False)

    roles = db.relationship('Role', secondary='user_role', backref='users')


class Role(db.Model):
    __tablename__ = 'role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)


class UserRole(db.Model):
    __tablename__ = 'user_role'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)


class ParkingLot(db.Model):
    __tablename__ = 'parking_lot'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(500), nullable=False)
    pin_code = db.Column(db.String(6), nullable=False)
    max_num_spots = db.Column(db.Integer, nullable=False)

    parkingspot = db.relationship('ParkingSpot', backref='lot',cascade='all, delete-orphan',single_parent=True)


class ParkingSpot(db.Model):
    __tablename__ = 'parking_spot'

    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id',ondelete = 'CASCADE'), nullable=False)
    status = db.Column(db.String(1), nullable=False)
    
    __table_args__ = (
        db.CheckConstraint("status IN ('A', 'O')", name='check_status_valid'),
    )

    


class ReserveParkingSpot(db.Model):
    __tablename__ = 'reserve_parking_spot'

    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=True)
    lot_id = db.Column(db.Integer,db.ForeignKey('parking_lot.id'), nullable=True)
    lot_name = db.Column(db.String(120),nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parking_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    leaving_timestamp = db.Column(db.DateTime, nullable=True)
    parking_cost_per_hour = db.Column(db.Float, nullable=False)

    user = db.relationship('User', backref='reservations')
    spot = db.relationship('ParkingSpot', backref='reservations')
