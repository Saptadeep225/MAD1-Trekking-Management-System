from flask import Blueprint, jsonify
from models import db, User, Trek, Booking

api = Blueprint("api", __name__, url_prefix="/api")


@api.route("/treks")
def get_all_treks():
    treks = Trek.query.all()
    return jsonify([
        {
            "id": trek.id,
            "name": trek.name,
            "location": trek.location,
            "difficulty": trek.difficulty,
            "duration": trek.duration,
            "total_slots": trek.total_slots,
            "available_slots": trek.available_slots,
            "assigned_staff": trek.assigned_staff,
            "start_date": str(trek.start_date),
            "end_date": str(trek.end_date),
            "status": trek.status,
            "description": trek.description
        }
        for trek in treks
    ])


@api.route("/treks/<int:id>")
def get_single_trek(id):
    trek = Trek.query.get_or_404(id)
    return jsonify(
        {
            "id": trek.id,
            "name": trek.name,
            "location": trek.location,
            "difficulty": trek.difficulty,
            "duration": trek.duration,
            "total_slots": trek.total_slots,
            "available_slots": trek.available_slots,
            "assigned_staff": trek.assigned_staff,
            "start_date": str(trek.start_date),
            "end_date": str(trek.end_date),
            "status": trek.status,
            "description": trek.description
        }
    )


@api.route("/users")
def get_users():
    users = User.query.filter_by(role="user").all()
    return jsonify([
        {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "status": user.status
        }
        for user in users
    ])


@api.route("/staff")
def get_staff():
    staff = User.query.filter_by(role="staff").all()
    return jsonify([
        {
            "id": member.id,
            "username": member.username,
            "name": member.name,
            "email": member.email,
            "phone": member.phone,
            "status": member.status
        }
        for member in staff
    ])


@api.route("/bookings")
def get_bookings():
    bookings = Booking.query.all()
    return jsonify([
        {
            "id": booking.id,
            "user_id": booking.user_id,
            "trek_id": booking.trek_id,
            "booking_date": str(booking.booking_date),
            "number_of_people": booking.number_of_people,
            "status": booking.status
        }
        for booking in bookings
    ])