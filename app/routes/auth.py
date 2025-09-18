from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User, Role
from flask_mail import Message
from app import mail
import re

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form.get("firstname")
        last_name = request.form.get("lastname")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        role = request.form.get("role")

        if len(password) < 8:
           flash("Password must be at least 8 characters long.","info")
           return render_template("register.html")
        
        if not re.search(r"[A-Z]", password):
            flash("Password must contain at least one uppercase letter.","info")
            return render_template("register.html")

        if not re.search(r"[!@#$%^&*()_+{}\[\]:;<>,.?~\\-]", password):
            flash("Password must contain at least one special character.","info")
            return render_template("register.html")
        
        if not re.search(r"[a-z]", password):
            flash("Password must contain at least one lowercase letter.","info")
            return render_template("register.html")

        if not re.search(r"[0-9]", password):
            flash("Password must contain at least one number.","info")
            return render_template("register.html")

        if User.query.filter_by(email=email).first():
            flash("Email already registered.","error","info")
            return redirect(url_for("auth.register"))
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with this email already exists. Please login or use a different email.","error")
            return render_template("register.html")

        if not all([first_name, last_name, email, password, confirm_password]):
            flash("All fields are required.","info")
            return render_template("register.html")
        
        full_name = f"{first_name} {last_name}"

        user = User(
            name=full_name,
            email=email,
            role=role.strip().upper()
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        flash("Account created! Please wait for admin approval.",'success')
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
            flash("Invalid email or password.","error")
            return redirect(url_for("auth.login"))

        if not user.is_active:
            flash("Your account is not active yet. Contact admin.","error")
            return redirect(url_for("auth.login"))

        # ✅ At this point user is valid
        session["user_id"] = user.id
        # NEW (match what home() expects)
        session["role"] = user.role if isinstance(user.role, str) else user.role.value
        print("🧭 user.role from DB:", user.role, type(user.role))
        session['user_name'] = user.name



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
    flash("Logged out successfully.",'success')
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

@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("No account found with that email.", "danger")
            return redirect(url_for("auth.forgot_password"))

        # Generate token
        token = user.get_reset_token()

        # Send email
        reset_link = url_for("auth.reset_password", token=token, _external=True)
        msg = Message("Password Reset Request",
                      sender="your_email@gmail.com",
                      recipients=[user.email])
        msg.body = f"""Hi {user.name},

To reset your password, click the link below:
{reset_link}

If you did not request this, please ignore this email.
"""
        mail.send(msg)

        flash("Password reset instructions have been sent to your email.", "info")
        return redirect(url_for("auth.login"))

    return render_template("forgot_password.html")

@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = User.verify_reset_token(token)
    if not user:
        flash("That reset link is invalid or has expired.", "error")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        new_password = request.form.get("new_password")
        user.set_password(new_password)
        db.session.commit()
        flash("Your password has been updated!", "success")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html")



