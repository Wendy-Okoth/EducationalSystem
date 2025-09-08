from flask import Blueprint, render_template, session, redirect, url_for

student_bp = Blueprint("student", __name__, url_prefix="/student")

@student_bp.route("/dashboard")
def dashboard():
    # Make sure only logged-in students can view this
    if "role" not in session or session["role"] != "STUDENT":
        return redirect(url_for("auth.login"))

    return render_template("student_dashboard.html")
