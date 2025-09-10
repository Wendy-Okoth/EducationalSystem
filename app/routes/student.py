from flask import Blueprint, render_template, session, redirect, url_for
from app.models import User   # adjust if your models file is in a different place


student_bp = Blueprint("student", __name__, url_prefix="/student")

@student_bp.route("/dashboard")
def dashboard():
    # Make sure only logged-in students can view this
    if "role" not in session or session["role"] != "STUDENT":
     return redirect(url_for("auth.login"))
    
    student_id = session.get("user_id")   # assuming you store this at login
    student = User.query.get(student_id)  # replace `User` with your actual Student model

    return render_template("student_dashboard.html")

@student_bp.route("/edit-profile")
def edit_profile():
    if "role" not in session or session["role"] != "STUDENT":
        return redirect(url_for("auth.login"))
    return render_template("edit_profile.html") 

@student_bp.route("/calendar")
def calendar():
    if "role" not in session or session["role"] != "STUDENT":
        return redirect(url_for("auth.login"))
    return render_template("student_calendar.html")  

# Subject page
@student_bp.route("/subject/<int:subject_id>")
def subject(subject_id):
    if "role" not in session or session["role"] != "STUDENT":
        return redirect(url_for("auth.login"))

    # For now, just dummy data until you connect DB
    subjects = {
        1: "Mathematics",
        2: "English",
        3: "Science"
    }
    subject_name = subjects.get(subject_id, "Unknown Subject")

    return render_template("student_subject.html", subject_name=subject_name, subject_id=subject_id)

@student_bp.route("/subjects")
def subjects():
    if "role" not in session or session["role"] != "STUDENT":
        return redirect(url_for("auth.login"))

    subjects = [
        {"id": 1, "name": "Mathematics"},
        {"id": 2, "name": "English"},
        {"id": 3, "name": "Science"},
    ]
    return render_template("student_subjects.html", subjects=subjects)

@student_bp.route("/profile")
def profile():
    # Later you can pass actual student data from DB
    return render_template("student/profile.html")
