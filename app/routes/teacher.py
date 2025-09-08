from flask import Blueprint, render_template, session, redirect, url_for

teacher_bp = Blueprint("teacher", __name__, url_prefix="/teacher")

@teacher_bp.route("/dashboard")
def dashboard():
    if "role" not in session or session["role"] != "TEACHER":
        return redirect(url_for("auth.login"))

    return render_template("teacher_dashboard.html")
