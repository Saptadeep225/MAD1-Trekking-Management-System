from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth = Blueprint("auth", __name__)


@auth.route("/")
def index():
    if current_user.is_authenticated:
        if current_user.role == "admin":
            return redirect(url_for("admin.admin_dashboard"))
        elif current_user.role == "staff":
            return redirect(url_for("staff.staff_dashboard"))
        else:
            return redirect(url_for("user.dashboard"))
    return render_template("home.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth.index"))

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            if user.status == "blacklisted":
                flash("Your account has been blacklisted by the administrator.", "danger")
                return redirect(url_for("auth.login"))
            if user.role == "staff" and user.status == "pending":
                flash("Your account is waiting for admin approval.","warning")
                return redirect(url_for("auth.login"))
            login_user(user)
            flash(f"Welcome back, {user.name}!","success")
            if user.role == "admin":
                return redirect(url_for("admin.admin_dashboard"))
            elif user.role == "staff":
                return redirect(url_for("staff.staff_dashboard"))
            else:
                return redirect(url_for("user.dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("auth/login.html")


@auth.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("auth.index"))

    if request.method == "POST":
        username = request.form["username"].strip()
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        phone = request.form["phone"].strip()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        role = request.form["role"]

        if not username or not name or not email or not password:
            flash("Please fill all required fields.", "danger")
            return redirect(url_for("auth.register"))
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.register"))
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return redirect(url_for("auth.register"))
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return redirect(url_for("auth.register"))
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return redirect(url_for("auth.register"))
        status = "pending" if role == "staff" else "approved"
        new_user = User(
            username=username,
            name=name,
            email=email,
            phone=phone,
            password=generate_password_hash(password),
            role=role,
            status=status
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please login.","success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.","info")
    return redirect(url_for("auth.login"))