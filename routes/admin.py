from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, User, Trek, Booking
from datetime import datetime


admin = Blueprint("admin",__name__,url_prefix="/admin")



def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))

        if current_user.role != "admin":
            flash("Access Denied!", "danger")
            return redirect(url_for("auth.login"))

        return func(*args, **kwargs)

    return wrapper



@admin.route("/dashboard")
@login_required
@admin_required
def admin_dashboard():
    total_users = User.query.filter_by(role="user").count()
    total_staff = User.query.filter_by(role="staff").count()
    total_treks = Trek.query.count()
    total_bookings = Booking.query.count()
    pending_staff = User.query.filter_by(
        role="staff",
        status="pending"
    ).count()

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_staff=total_staff,
        total_treks=total_treks,
        total_bookings=total_bookings,
        pending_staff=pending_staff
    )



@admin.route("/users")
@login_required
@admin_required
def users():
    search = request.args.get("search", "")
    if search:
        users = User.query.filter(
            User.role == "user",
            User.name.contains(search)
        ).all()
    else:
        users = User.query.filter_by(role="user").all()
    return render_template("admin/users.html",users=users,search=search)


@admin.route("/users/blacklist/<int:id>")
@login_required
@admin_required
def blacklist_user(id):
    user = User.query.get_or_404(id)
    user.status = "blacklisted"
    db.session.commit()
    flash("User blacklisted.", "warning")
    return redirect(url_for("admin.users"))


@admin.route("/users/unblacklist/<int:id>")
@login_required
@admin_required
def unblacklist_user(id):
    user = User.query.get_or_404(id)
    user.status = "approved"
    db.session.commit()
    flash("User restored.", "success")
    return redirect(url_for("admin.users"))



@admin.route("/staff")
@login_required
@admin_required
def staff():
    search = request.args.get("search", "")
    if search:
        staff = User.query.filter(
            User.role == "staff",
            User.name.contains(search)
        ).all()
    else:
        staff = User.query.filter_by(role="staff").all()
    return render_template(
        "admin/staff.html",
        staff=staff,
        search=search
    )


@admin.route("/staff/approve/<int:id>")
@login_required
@admin_required
def approve_staff(id):
    staff = User.query.get_or_404(id)
    staff.status = "approved"
    db.session.commit()
    flash("Staff approved successfully.", "success")
    return redirect(url_for("admin.staff"))


@admin.route("/staff/blacklist/<int:id>")
@login_required
@admin_required
def blacklist_staff(id):
    staff = User.query.get_or_404(id)
    staff.status = "blacklisted"
    db.session.commit()
    flash("Staff blacklisted.", "warning")
    return redirect(url_for("admin.staff"))


@admin.route("/staff/unblacklist/<int:id>")
@login_required
@admin_required
def unblacklist_staff(id):
    staff = User.query.get_or_404(id)
    staff.status = "approved"
    db.session.commit()
    flash("Staff restored successfully.", "success")
    return redirect(url_for("admin.staff"))


@admin.route("/treks")
@login_required
@admin_required
def treks():
    search = request.args.get("search", "")
    if search:
        treks = Trek.query.filter(
            Trek.name.contains(search)
        ).all()
    else:
        treks = Trek.query.all()
    return render_template(
        "admin/treks.html",
        treks=treks,
        search=search
    )


@admin.route("/treks/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_trek():
    if request.method == "POST":
        trek = Trek(
            name=request.form["name"],
            location=request.form["location"],
            difficulty=request.form["difficulty"],
            duration=int(request.form["duration"]),
            total_slots=int(request.form["total_slots"]),
            available_slots=int(request.form["available_slots"]),
            start_date=datetime.strptime(
                request.form["start_date"],
                "%Y-%m-%d"
            ).date(),
            end_date=datetime.strptime(
                request.form["end_date"],
                "%Y-%m-%d"
            ).date(),
            description=request.form["description"]
        )
        db.session.add(trek)
        db.session.commit()
        flash("Trek added successfully.", "success")
        return redirect(url_for("admin.treks"))
    return render_template(
        "admin/trek_form.html",
        trek=None
    )

@admin.route("/treks/assign/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def assign_staff(id):
    trek = Trek.query.get_or_404(id)
    staff_list = User.query.filter_by(
        role="staff",
        status="approved"
    ).all()

    if request.method == "POST":
        staff_id = request.form.get("staff_id")
        if staff_id:
            trek.assigned_staff = int(staff_id)
        else:
            trek.assigned_staff = None

        db.session.commit()
        flash("Staff assigned successfully.", "success")
        return redirect(url_for("admin.treks"))

    return render_template(
        "admin/assign_staff.html",
        trek=trek,
        staff_list=staff_list
    )


@admin.route("/treks/edit/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_trek(id):
    trek = Trek.query.get_or_404(id)
    if request.method == "POST":
        trek.name = request.form["name"]
        trek.location = request.form["location"]
        trek.difficulty = request.form["difficulty"]
        trek.duration = int(request.form["duration"])
        trek.total_slots = int(request.form["total_slots"])
        trek.available_slots = int(request.form["available_slots"])
        trek.start_date = datetime.strptime(
            request.form["start_date"],
            "%Y-%m-%d"
        ).date()
        trek.end_date = datetime.strptime(
            request.form["end_date"],
            "%Y-%m-%d"
        ).date()
        trek.description = request.form["description"]
        db.session.commit()
        flash("Trek updated successfully.", "success")
        return redirect(url_for("admin.treks"))
    return render_template(
        "admin/trek_form.html",
        trek=trek
    )


@admin.route("/treks/delete/<int:id>")
@login_required
@admin_required
def delete_trek(id):
    trek = Trek.query.get_or_404(id)
    trek.is_deleted = True
    db.session.commit()
    flash("Trek removed.", "warning")
    return redirect(url_for("admin.treks"))


@admin.route("/treks/restore/<int:id>")
@login_required
@admin_required
def restore_trek(id):
    trek = Trek.query.get_or_404(id)
    trek.is_deleted = False
    db.session.commit()
    flash("Trek restored.", "success")
    return redirect(url_for("admin.treks"))
@admin.route("/bookings")
@login_required
@admin_required
def bookings():
    search = request.args.get("search", "")
    if search:
        bookings = Booking.query.join(User, Booking.user_id == User.id).join(Trek, Booking.trek_id == Trek.id).filter(
            (User.name.contains(search)) |
            (Trek.name.contains(search))
        ).all()
    else:
        bookings = Booking.query.all()
    return render_template(
        "admin/bookings.html",
        bookings=bookings,
        search=search
    )