from flask import Blueprint, render_template, session, redirect, url_for , request , jsonify
from app.models import User, Role , Subject , db ,  Assignment , Notification , CompletedAssignment
from app import db
from flask_login import current_user, login_required

student_bp = Blueprint("student", __name__, url_prefix="/student")

def is_student():
    """Helper function to check if the user has a student role."""
    return session.get('role') == 'STUDENT'

@student_bp.route('/dashboard')
def dashboard():
    if not is_student():
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
    if not is_student():
        return redirect(url_for("auth.login"))
    return render_template("student_calendar.html") 

# Subject page
@student_bp.route("/subject/<int:subject_id>")
def subject(subject_id):
    if not is_student():
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
    if not is_student():
        return redirect(url_for("auth.login"))

    subjects = [
        {"id": 1, "name": "Mathematics"},
        {"id": 2, "name": "English"},
        {"id": 3, "name": "Science"},
    ]
    return render_template("student_subjects.html", subjects=subjects)

@student_bp.route("/profile")
def profile():
    student_id = session.get("user_id")
    
    if not student_id:
        return redirect(url_for("auth.login"))

    student = User.query.filter_by(id=student_id, role=Role.STUDENT).first()

    if not student:
        return "Student not found", 404
    return render_template("profile.html", student=student)

@student_bp.route('/search_subjects')
def search_subjects():
    """Route to search for subjects in the database."""
    if not is_student():
        return jsonify({'success': False, 'message': 'Authentication required.'}), 401
    
    query = request.args.get('query', '')
    subjects = Subject.query.filter(Subject.name.ilike(f'%{query}%')).all()
    results = [{'id': s.id, 'name': s.name} for s in subjects]
    return jsonify(results)

@student_bp.route('/add_subject', methods=['POST'])
def add_subject():
    """Route to enroll a student in a subject using an enrollment key."""
    # Add a manual session check to ensure the user is logged in
    if not is_student():
        return jsonify({'success': False, 'message': 'Authentication required.'}), 401

    data = request.json
    subject_id = data.get('subject_id')
    enrollment_key = data.get('enrollment_key')

    if not subject_id or not enrollment_key:
        return jsonify({'success': False, 'message': 'Missing subject ID or enrollment key.'})

    subject_to_add = Subject.query.get(subject_id)

    if not subject_to_add:
        return jsonify({'success': False, 'message': 'Subject not found.'})

    # Validate the enrollment key
    if subject_to_add.enrollment_key != enrollment_key:
        return jsonify({'success': False, 'message': 'Invalid enrollment key.'})

    # Get the current user from the session
    current_user = User.query.get(session['user_id'])

    # Check if the user is already enrolled
    if subject_to_add in current_user.enrolled_subjects:
        return jsonify({'success': False, 'message': 'You are already enrolled in this subject.'})

    # If the key is valid and not already enrolled, add the subject
    current_user.enrolled_subjects.append(subject_to_add)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Successfully enrolled!'})

@student_bp.route('/api/assignments')
def get_student_assignments():
    if not is_student():
        return jsonify([])

    student = User.query.get(session.get('user_id'))
    if not student:
        return jsonify([])

    # Get all assignments for subjects the student is enrolled in
    enrolled_subjects = student.enrolled_subjects
    assignments_data = []

    for enrollment in enrolled_subjects:
        subject_assignments = Assignment.query.filter_by(subject_id=enrollment.subject_id).all()
        for assignment in subject_assignments:
            assignments_data.append({
                'title': f"Assignment: {assignment.title}",
                'start': assignment.due_date.isoformat(),
                'end': assignment.due_date.isoformat(),
                'allDay': False
            })

    return jsonify(assignments_data)

@student_bp.route('/api/notifications')
def get_unread_notifications():
    """API endpoint to get the count of unread notifications for the student."""
    if not is_student():
        return jsonify({'count': 0}), 401

    unread_count = Notification.query.filter_by(user_id=session['user_id'], is_read=False).count()

    return jsonify({'count': unread_count})

@student_bp.route('/api/notifications/all')
def get_all_notifications():
    """API endpoint to get all notifications for a student."""
    if not is_student():
        return jsonify([]), 401

    notifications = Notification.query.filter_by(user_id=session['user_id']).order_by(Notification.created_at.desc()).all()
    
    notifications_data = [{
        'id': n.id,
        'message': n.message,
        'is_read': n.is_read,
        'timestamp': n.created_at.isoformat()
    } for n in notifications]
    
    return jsonify(notifications_data)

@student_bp.route('/notifications')
def notifications():
    if not is_student():
        return redirect(url_for('auth.login'))
    # This will render a new template to display all notifications
    return render_template('student_notifications.html')

@student_bp.route('/api/progress')
def get_student_progress():
    if not is_student():
        return jsonify({})

    student = User.query.get(session.get('user_id'))
    if not student:
        return jsonify({})

    progress_data = {}
    
    # Get all subjects the student is enrolled in
    enrolled_subjects = [e.subject for e in student.enrolled_subjects]

    for subject in enrolled_subjects:
        total_assignments = Assignment.query.filter_by(subject_id=subject.id).count()
        
        # Count assignments completed by the student for this subject
        completed_assignments = CompletedAssignment.query.filter(
            CompletedAssignment.student_id == student.id,
            CompletedAssignment.assignment_id.in_(
                db.session.query(Assignment.id).filter(Assignment.subject_id == subject.id)
            )
        ).count()

        completion_percentage = 0
        if total_assignments > 0:
            completion_percentage = (completed_assignments / total_assignments) * 100

        progress_data[subject.id] = {
            'subject_name': subject.name,
            'completed': completed_assignments,
            'total': total_assignments,
            'percentage': round(completion_percentage, 2)
        }
    
    return jsonify(progress_data)