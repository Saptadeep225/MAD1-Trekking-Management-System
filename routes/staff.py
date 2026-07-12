from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Trek, Booking, User

staff = Blueprint("staff", __name__, url_prefix="/staff")



def staff_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        if current_user.role != "staff":
            flash("Access Denied!", "danger")
            return redirect(url_for("auth.login"))
        if current_user.status != "approved":
            flash("Your account is awaiting admin approval.", "warning")
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)
    return wrapper



@staff.route("/dashboard")
@login_required
@staff_required
def staff_dashboard():

    assigned_treks = Trek.query.filter_by(
        assigned_staff=current_user.id
    ).count()

    total_participants = Booking.query.join(Trek).filter(
        Trek.assigned_staff == current_user.id
    ).count()

    return render_template(
        "staff/dashboard.html",
        assigned_treks=assigned_treks,
        total_participants=total_participants
    )


@staff.route("/treks/update/<int:id>", methods=["GET", "POST"])
@login_required
@staff_required
def update_trek(id):
    trek = Trek.query.get_or_404(id)
    if trek.assigned_staff != current_user.id:
        flash("Access Denied!", "danger")
        return redirect(url_for("staff.assigned_treks"))
    
    booked_slots = Booking.query.filter_by(trek_id=trek.id, status="Booked").count()
    if request.method == "POST":
        try:
            available_slots = int(request.form["available_slots"])
            if available_slots < 0:
                flash("Available slots cannot be negative.", "danger")
                return render_template("staff/edit_trek.html", trek=trek, booked_slots=booked_slots)
            
            max_allowed_available = trek.total_slots - booked_slots
            if available_slots > max_allowed_available:
                flash(f"Available slots cannot exceed {max_allowed_available} (Total Slots minus current active bookings).", "danger")
                return render_template("staff/edit_trek.html", trek=trek, booked_slots=booked_slots)
            
            trek.available_slots = available_slots
            new_status = request.form["status"]
            trek.status = new_status
            
            if new_status == "Completed":
                for booking in trek.bookings:
                    if booking.status == "Booked":
                        booking.status = "Completed"
            
            db.session.commit()
            flash("Trek updated successfully.", "success")
            return redirect(url_for("staff.assigned_treks"))
        except ValueError:
            flash("Invalid slots format.", "danger")
            return render_template("staff/edit_trek.html", trek=trek, booked_slots=booked_slots)
    return render_template(
        "staff/edit_trek.html",
        trek=trek,
        booked_slots=booked_slots
    )


@staff.route("/treks")
@login_required
@staff_required
def assigned_treks():
    treks = Trek.query.filter_by(
        assigned_staff=current_user.id
    ).all()
    return render_template(
        "staff/assigned_treks.html",
        treks=treks
    )



@staff.route("/participants/<int:id>")
@login_required
@staff_required
def participants(id):
    trek = Trek.query.get_or_404(id)
    if trek.assigned_staff != current_user.id:
        flash("Access Denied!", "danger")
        return redirect(url_for("staff.assigned_treks"))
    bookings = Booking.query.filter_by(
        trek_id=id
    ).all()
    return render_template(
        "staff/participants.html",
        trek=trek,
        bookings=bookings
    )