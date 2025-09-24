from flask import Blueprint, render_template, session, redirect, url_for , request
from app.models import User , db , Subject , SubjectContent


teacher_bp = Blueprint("teacher", __name__, url_prefix="/teacher")

def is_teacher():
    """Helper function to check if the user has a teacher role."""
    return session.get('role') == 'TEACHER'

@teacher_bp.route('/dashboard')
def dashboard():
    if not is_teacher():
        return redirect(url_for('auth.login'))

    teacher = User.query.get(session['user_id'])
    
    return render_template('teacher_dashboard.html', teacher=teacher)


@teacher_bp.route('/profile')
def profile():
    if not is_teacher():
        return redirect(url_for("auth.login"))
    
    teacher_id = session.get("user_id")
    teacher = User.query.get(teacher_id)

    if not teacher:
        return "Teacher not found", 404

    subjects = teacher.subjects
    courses = teacher.courses if hasattr(teacher, "courses") else []

    return render_template("teacher_profile.html", teacher=teacher)


@teacher_bp.route('/calendar')
def calendar():
    if not is_teacher():
        return redirect(url_for("auth.login"))
    return render_template("calendar.html")


@teacher_bp.route('/subjects')
def subjects():
    if not is_teacher():
        return redirect(url_for("auth.login"))
    return render_template("subjects.html")


# New route to add subject content
@teacher_bp.route('/add_content', methods=['GET', 'POST'])
def add_content():
    if not is_teacher():
        return redirect(url_for('auth.login'))

    subjects = Subject.query.all()

    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        title = request.form.get('title')
        content_body = request.form.get('content_body')

        if not subject_id or not title or not content_body:
            return "Missing form data!", 400

        # Create a new SubjectContent object
        new_content = SubjectContent(
            title=title,
            content_body=content_body,
            subject_id=subject_id
        )
        
        db.session.add(new_content)
        db.session.commit()
        
        # Redirect to prevent form resubmission
        return redirect(url_for('teacher.add_content'))
    
    return render_template('add_content.html', subjects=subjects)