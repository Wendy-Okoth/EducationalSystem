from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User, Role

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        if User.query.filter_by(email=email).first():
            flash("Email already registered.")
            return redirect(url_for("auth.register"))

        user = User(
            name=name,
            email=email,
            role=role
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        flash("Account created! Please wait for admin approval.")
        return redirect(url_for("auth.login"))

    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("Invalid email or password.")
            return redirect(url_for("auth.login"))

        if not user.is_active:
            flash("Your account is not active yet. Contact admin.")
            return redirect(url_for("auth.login"))

        session["user_id"] = user.id
        session["role"] = user.role

        # Redirect based on role
        if user.role == Role.STUDENT:
            return redirect(url_for("student.dashboard"))
        elif user.role == Role.TEACHER:
            return redirect(url_for("teacher.dashboard"))
        elif user.role == Role.ADMIN:
            return redirect(url_for("admin.dashboard"))

    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for("auth.login"))
