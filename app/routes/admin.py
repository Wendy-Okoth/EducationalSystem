from flask import Blueprint, render_template, session, redirect, url_for

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/dashboard")
def dashboard():
    if "role" not in session or session["role"] != "ADMIN":
        return redirect(url_for("auth.login"))

    return render_template("admin_dashboard.html")
