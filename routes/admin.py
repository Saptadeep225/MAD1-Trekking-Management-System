from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, User, Trek, Booking
from datetime import datetime, date

class DummyTrek:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if k in ['total_slots', 'available_slots', 'duration'] and v is not None:
                try:
                    v = int(v)
                except (ValueError, TypeError):
                    v = 0
            setattr(self, k, v)



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
        name = request.form.get("name", "").strip()
        location = request.form.get("location", "").strip()
        difficulty = request.form.get("difficulty", "Easy")
        duration_str = request.form.get("duration", "")
        total_slots_str = request.form.get("total_slots", "")
        available_slots_str = request.form.get("available_slots", "")
        start_date_str = request.form.get("start_date", "")
        end_date_str = request.form.get("end_date", "")
        description = request.form.get("description", "").strip()

        # Construct dummy object to return to form on failure
        temp_trek = DummyTrek(
            name=name,
            location=location,
            difficulty=difficulty,
            duration=duration_str,
            total_slots=total_slots_str,
            available_slots=available_slots_str,
            start_date=start_date_str,
            end_date=end_date_str,
            description=description
        )

        if not name:
            flash("Trek Name cannot be empty.", "danger")
            return render_template("admin/trek_form.html", trek=temp_trek)
        if not location:
            flash("Location cannot be empty.", "danger")
            return render_template("admin/trek_form.html", trek=temp_trek)
        if not description:
            flash("Description cannot be empty.", "danger")
            return render_template("admin/trek_form.html", trek=temp_trek)
        if difficulty not in ["Easy", "Moderate", "Hard"]:
            flash("Invalid difficulty level selection.", "danger")
            return render_template("admin/trek_form.html", trek=temp_trek)

        try:
            duration = int(duration_str)
            total_slots = int(total_slots_str)
            available_slots = int(available_slots_str)
        except ValueError:
            flash("Duration, Total Slots, and Available Slots must be valid integers.", "danger")
            return render_template("admin/trek_form.html", trek=temp_trek)

        if duration <= 0:
            flash("Duration must be at least 1 day.", "danger")
            return render_template("admin/trek_form.html", trek=temp_trek)
        if total_slots <= 0:
            flash("Total Slots must be at least 1.", "danger")
            return render_template("admin/trek_form.html", trek=temp_trek)
        if available_slots < 0:
            flash("Available Slots cannot be negative.", "danger")
            return render_template("admin/trek_form.html", trek=temp_trek)
        if available_slots > total_slots:
            flash("Available Slots cannot exceed Total Slots.", "danger")
            return render_template("admin/trek_form.html", trek=temp_trek)

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.", "danger")
            return render_template("admin/trek_form.html", trek=temp_trek)

        if start_date < date.today():
            flash("Start Date cannot be in the past.", "danger")
            return render_template("admin/trek_form.html", trek=temp_trek)
        if end_date <= start_date:
            flash("End Date must be after the Start Date.", "danger")
            return render_template("admin/trek_form.html", trek=temp_trek)
        if duration != (end_date - start_date).days:
            flash(f"Duration must match the difference between Start and End dates ({(end_date - start_date).days} days).", "danger")
            return render_template("admin/trek_form.html", trek=temp_trek)

        trek = Trek(
            name=name,
            location=location,
            difficulty=difficulty,
            duration=duration,
            total_slots=total_slots,
            available_slots=available_slots,
            start_date=start_date,
            end_date=end_date,
            description=description
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
    booked_slots = Booking.query.filter_by(trek_id=trek.id, status="Booked").count()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        location = request.form.get("location", "").strip()
        difficulty = request.form.get("difficulty", "Easy")
        duration_str = request.form.get("duration", "")
        total_slots_str = request.form.get("total_slots", "")
        available_slots_str = request.form.get("available_slots", "")
        start_date_str = request.form.get("start_date", "")
        end_date_str = request.form.get("end_date", "")
        description = request.form.get("description", "").strip()

        temp_trek = DummyTrek(
            id=trek.id,
            name=name,
            location=location,
            difficulty=difficulty,
            duration=duration_str,
            total_slots=total_slots_str,
            available_slots=available_slots_str,
            start_date=start_date_str,
            end_date=end_date_str,
            description=description
        )

        if not name:
            flash("Trek Name cannot be empty.", "danger")
            return render_template("admin/trek_form.html", trek=temp_trek, booked_slots=booked_slots)
        if not location:
            flash("Location cannot be empty.", "danger")
            return render_template("admin/trek_form.html", trek=temp_trek, booked_slots=booked_slots)
        if not description:
            flash("Description cannot be empty.", "danger")
            return render_template("admin/trek_form.html", trek=temp_trek, booked_slots=booked_slots)
        if difficulty not in ["Easy", "Moderate", "Hard"]:
            flash("Invalid difficulty level selection.", "danger")
            return render_template("admin/trek_form.html", trek=temp_trek, booked_slots=booked_slots)

        try:
            duration = int(duration_str)
            total_slots = int(total_slots_str)
            available_slots = int(available_slots_str)
        except ValueError:
            flash("Duration, Total Slots, and Available Slots must be valid integers.", "danger")
            return render_template("admin/trek_form.html", trek=temp_trek, booked_slots=booked_slots)

        if duration <= 0:
            flash("Duration must be at least 1 day.", "danger")
            return render_template("admin/trek_form.html", trek=temp_trek, booked_slots=booked_slots)
        if total_slots <= 0:
            flash("Total Slots must be at least 1.", "danger")
            return render_template("admin/trek_form.html", trek=temp_trek, booked_slots=booked_slots)
        if available_slots < 0:
            flash("Available Slots cannot be negative.", "danger")
            return render_template("admin/trek_form.html", trek=temp_trek, booked_slots=booked_slots)
        if available_slots > total_slots:
            flash("Available Slots cannot exceed Total Slots.", "danger")
            return render_template("admin/trek_form.html", trek=temp_trek, booked_slots=booked_slots)

        if total_slots < booked_slots:
            flash(f"Total Slots ({total_slots}) cannot be less than current active bookings ({booked_slots}).", "danger")
            return render_template("admin/trek_form.html", trek=temp_trek, booked_slots=booked_slots)

        max_allowed_available = total_slots - booked_slots
        if available_slots > max_allowed_available:
            flash(f"Available Slots ({available_slots}) cannot exceed {max_allowed_available} (Total Slots minus current active bookings).", "danger")
            return render_template("admin/trek_form.html", trek=temp_trek, booked_slots=booked_slots)

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.", "danger")
            return render_template("admin/trek_form.html", trek=temp_trek, booked_slots=booked_slots)

        if end_date <= start_date:
            flash("End Date must be after the Start Date.", "danger")
            return render_template("admin/trek_form.html", trek=temp_trek, booked_slots=booked_slots)
        if duration != (end_date - start_date).days:
            flash(f"Duration must match the difference between Start and End dates ({(end_date - start_date).days} days).", "danger")
            return render_template("admin/trek_form.html", trek=temp_trek, booked_slots=booked_slots)

        if start_date != trek.start_date and start_date < date.today():
            flash("New Start Date cannot be in the past.", "danger")
            return render_template("admin/trek_form.html", trek=temp_trek, booked_slots=booked_slots)

        trek.name = name
        trek.location = location
        trek.difficulty = difficulty
        trek.duration = duration
        trek.total_slots = total_slots
        trek.available_slots = available_slots
        trek.start_date = start_date
        trek.end_date = end_date
        trek.description = description
        db.session.commit()
        flash("Trek updated successfully.", "success")
        return redirect(url_for("admin.treks"))
    return render_template(
        "admin/trek_form.html",
        trek=trek,
        booked_slots=booked_slots
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