from functools import wraps
from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
)

from flask_login import login_required, current_user
from models import db, Trek, Booking


user = Blueprint("user",__name__,url_prefix="/user")


#====================================
# Helper Functions
#====================================

def user_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        if current_user.role != "user":
            flash("Access Denied!", "danger")
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)
    return wrapper


#====================================
# Dashboard
#====================================

@user.route("/dashboard")
@login_required
@user_required
def dashboard():
    total_bookings = Booking.query.filter_by(
        user_id=current_user.id
    ).count()
    upcoming = Booking.query.filter_by(
        user_id=current_user.id,
        status="Booked"
    ).count()
    completed = Booking.query.filter_by(
        user_id=current_user.id,
        status="Completed"
    ).count()
    return render_template(
        "user/dashboard.html",
        total_bookings=total_bookings,
        upcoming=upcoming,
        completed=completed
    )


#====================================
# View Treks
#====================================

@user.route("/treks")
@login_required
@user_required
def treks():
    search = request.args.get("search", "")
    difficulty = request.args.get("difficulty", "")
    location = request.args.get("location", "")
    query = Trek.query.filter_by(status="Open")
    if search:
        query = query.filter(
            Trek.name.contains(search)
        )
    if difficulty:
        query = query.filter_by(
            difficulty=difficulty
        )
    if location:
        query = query.filter(
            Trek.location.contains(location)
        )
    treks = query.all()
    return render_template(
        "user/treks.html",
        treks=treks,
        search=search,
        difficulty=difficulty,
        location=location
    )

#====================================
# Book Trek
#====================================

@user.route("/book/<int:id>", methods=["POST"])
@login_required
@user_required
def book(id):
    trek = Trek.query.get_or_404(id)
    if trek.available_slots <= 0:
        flash("No slots available.", "danger")
        return redirect(url_for("user.treks"))
    booking = Booking(
        user_id=current_user.id,
        trek_id=trek.id,
        booking_date=datetime.now(),
        number_of_people=1,
        status="Booked"
    )

    existing = Booking.query.filter_by(
        user_id=current_user.id,
        trek_id=trek.id
    ).first()

    if existing:
        flash("You have already booked this trek.", "warning")
        return redirect(url_for("user.treks"))
    else:
        trek.available_slots -= 1
        db.session.add(booking)
        db.session.commit()
        flash("Booking Successful!", "success")
        return redirect(url_for("user.bookings"))


#====================================
# My Bookings
#====================================

@user.route("/bookings")
@login_required
@user_required
def bookings():
    bookings = Booking.query.filter_by(
        user_id=current_user.id
    ).all()
    return render_template(
        "user/bookings.html",
        bookings=bookings
    )


#====================================
# Profile
#====================================

@user.route("/profile", methods=["GET", "POST"])
@login_required
@user_required
def profile():
    if request.method == "POST":
        current_user.name = request.form["name"]
        current_user.phone = request.form["phone"]
        current_user.email = request.form["email"]
        db.session.commit()
        flash("Profile Updated!", "success")
        return redirect(url_for("user.profile"))
    return render_template(
        "user/profile.html"
    )