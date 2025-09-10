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
            role=role.strip().upper()
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

        print("📩 Email received from form:", email)
        print("🔑 Password received from form:", password)

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("Invalid email or password.")
            return redirect(url_for("auth.login"))

        if not user.is_active:
            flash("Your account is not active yet. Contact admin.")
            return redirect(url_for("auth.login"))

        # ✅ At this point user is valid
        session["user_id"] = user.id
        # NEW (match what home() expects)
        session["role"] = user.role if isinstance(user.role, str) else user.role.value
        print("🧭 user.role from DB:", user.role, type(user.role))



        # Redirect 
        # Redirect based on role (compare with strings)
        if user.role == "STUDENT":
           return redirect(url_for("student.dashboard"))
        elif user.role == "TEACHER":
           return redirect(url_for("teacher.dashboard"))
        elif user.role == "ADMIN":
             return redirect(url_for("admin.dashboard"))
        else:
             flash(f"Unknown role: {user.role}")
             return redirect(url_for("auth.login"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for("auth.login"))

@auth_bp.route("/")
def home():
    # If user is logged in, send them to the right dashboard
    if "role" in session:
        if session["role"] == "STUDENT":
            return redirect(url_for("student.dashboard"))
        elif session["role"] == "TEACHER":
            return redirect(url_for("teacher.dashboard"))
        elif session["role"] == "ADMIN":
            return redirect(url_for("admin.dashboard"))
    # Otherwise show login page
    return redirect(url_for("auth.login"))