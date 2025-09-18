from flask import Blueprint, render_template, session, redirect, url_for , request , jsonify
from app.models import User, Role , Subject , db   # adjust if your models file is in a different place
from app import db
from flask_login import current_user, login_required

student_bp = Blueprint("student", __name__, url_prefix="/student")

@student_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session or session.get('role') != 'STUDENT':
        return redirect(url_for('auth.login'))
    
    student = User.query.get(session['user_id'])
    
    return render_template('student_dashboard.html', student=student)

@student_bp.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():
    student_id = session.get("user_id")
    student = User.query.get(student_id)

    if request.method == "POST":
        student.name = request.form["name"]
        student.email = request.form["email"]
        db.session.commit()
        return redirect(url_for("student.profile"))
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
    student_id = session.get("user_id")  # user_id is stored in session after login
    
    if not student_id:
        return redirect(url_for("auth.login"))

    student = User.query.filter_by(id=student_id, role=Role.STUDENT).first()

    if not student:
        return "Student not found", 404
    return render_template("profile.html", student=student)

@student_bp.route('/search_subjects')
@login_required
def search_subjects():
    """Route to search for subjects in the database."""
    query = request.args.get('query', '')
    subjects = Subject.query.filter(Subject.name.ilike(f'%{query}%')).all()
    results = [{'id': s.id, 'name': s.name} for s in subjects]
    return jsonify(results)

@student_bp.route('/add_subject', methods=['POST'])
@login_required
def add_subject():
    """Route to add a subject to the student's enrollment."""
    data = request.json
    subject_id = data.get('subject_id')
    
    subject_to_add = Subject.query.get(subject_id)
    
    if subject_to_add:
        # Check if the user is already enrolled in the subject
        if subject_to_add not in current_user.enrolled_subjects:
            current_user.enrolled_subjects.append(subject_to_add)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Subject added!'})
        else:
            return jsonify({'success': False, 'message': 'Subject is already in your list.'})
    
    return jsonify({'success': False, 'message': 'Subject not found.'})
