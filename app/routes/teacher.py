from flask import Blueprint, render_template, session, redirect, url_for
from app.models import User


teacher_bp = Blueprint("teacher", __name__, url_prefix="/teacher")

@teacher_bp.route("/dashboard")
def dashboard():
    if "role" not in session or session["role"] != "TEACHER":
        return redirect(url_for("auth.login"))

    return render_template("teacher_dashboard.html")
   
@teacher_bp.route('/profile')
def profile():
    if "role" not in session or session["role"] != "TEACHER":
        return redirect(url_for("auth.login"))
    
    teacher_id = session.get("user_id")  # or however you store the logged-in teacher's ID
    teacher = User.query.get(teacher_id)

    if not teacher:
        return "Teacher not found", 404

    # Fetch subjects dynamically
    subjects = teacher.subjects  # thanks to the backref in the model
    # Fetch courses/classes dynamically if you have CourseAssignments
    courses = teacher.courses if hasattr(teacher, "courses") else []

    return render_template("teacher_profile.html", teacher=teacher)

@teacher_bp.route('/calendar')
def calendar():
    if "role" not in session or session["role"] != "TEACHER":
        return redirect(url_for("auth.login"))
    return render_template("calendar.html")

@teacher_bp.route('/subjects')
def subjects():
    if "role" not in session or session["role"] != "TEACHER":
        return redirect(url_for("auth.login"))
    return render_template("subjects.html")
