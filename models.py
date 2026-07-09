from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user")
    status = db.Column(db.String(20),default="approved")
    bookings = db.relationship("Booking", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"


class Trek(db.Model):
    __tablename__ = "trek"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    total_slots = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)

    assigned_staff = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True
    )

    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(20), default="Pending")
    is_deleted = db.Column(
        db.Boolean,
        default=False
    )

    description = db.Column(db.Text)
    bookings = db.relationship(
        "Booking",
        backref="trek",
        lazy=True
    )

    def __repr__(self):
        return f"<Trek {self.name}>"


class Booking(db.Model):
    __tablename__ = "booking"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    trek_id = db.Column(
        db.Integer,
        db.ForeignKey("trek.id"),
        nullable=False
    )

    booking_date = db.Column(db.DateTime)

    number_of_people = db.Column(
        db.Integer,
        default=1,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="Booked"
    )

    def __repr__(self):
        return f"<Booking {self.id}>"