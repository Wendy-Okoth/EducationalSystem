from flask import Blueprint, render_template, session, redirect, url_for , request , jsonify
from app.models import User, Role , Subject , db ,  Assignment , Notification , CompletedAssignment , Submission , SubjectContent
from app import db
from flask_login import current_user, login_required
from flask import render_template, redirect, url_for, session, jsonify, flash
from datetime import datetime, timedelta

student_bp = Blueprint("student", __name__, url_prefix="/student")

def is_student():
    """Helper function to check if the user has a student role."""
    return session.get('role') == 'STUDENT'

@student_bp.route('/dashboard')
def dashboard():
    if not is_student():
        return redirect(url_for('auth.login'))
    
    student = User.query.get(session['user_id'])
    
    # Get subjects for student's form
    student_form = getattr(student, 'form', None)
    if student_form:
        # Get subjects for the student's form that they're enrolled in
        enrolled_subjects = [s for s in student.enrolled_subjects if s.form == student_form]
    else:
        enrolled_subjects = student.enrolled_subjects
    
    return render_template('student_dashboard.html', 
                         student=student, 
                         subjects=enrolled_subjects,
                         student_form=student_form)

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


@student_bp.route("/subject/<int:subject_id>")
def subject_detail(subject_id):
    if not is_student():
        return redirect(url_for("auth.login"))
    
    student_id = session.get('user_id')
    student = User.query.get(student_id)
    subject = Subject.query.get_or_404(subject_id)
    
    # Verify enrollment
    if subject not in student.enrolled_subjects:
        flash("You are not enrolled in this subject.", "danger")
        return redirect(url_for('student.dashboard'))

    # Fetch materials using the correct model name: SubjectContent
    contents_query = SubjectContent.query.filter_by(subject_id=subject.id).all()

    # Fetch assignments
    assignments_query = Assignment.query.filter_by(subject_id=subject.id).order_by(Assignment.due_date.asc()).all()
    
    formatted_assignments = []
    for a in assignments_query:
        submission = Submission.query.filter_by(assignment_id=a.id, student_id=student_id).first()
        status = 'pending'
        if submission:
            status = 'completed'
        elif a.due_date < datetime.utcnow():
            status = 'overdue'
            
        formatted_assignments.append({
            'id': a.id,
            'title': a.title,
            'description': a.description,
            'due_date': a.due_date.strftime('%d %b, %Y %H:%M'),
            'status': status,
            'weight': getattr(a, 'weight', 0),
            'submitted_date': submission.submitted_at.strftime('%d %b, %H:%M') if submission else None
        })

    subject_info = {
        'id': subject.id,
        'name': subject.name,
        'code': subject.code,
        'description': subject.description,
        'teacher_name': subject.teacher.name if subject.teacher else "Not Assigned",
        'enrolled_date': "Active" 
    }

    return render_template('subject_detail.html', 
                           subject=subject_info, 
                           assignments=formatted_assignments,
                           contents=contents_query)

@student_bp.route("/calendar")
def calendar():
    if not is_student():
        return redirect(url_for("auth.login"))
    return render_template("student_calendar.html")

@student_bp.route('/api/calendar_events')
def calendar_events():
    if not is_student():
        return jsonify([])

    student_id = session.get('user_id')
    student = User.query.get(student_id)
    events = []
    
    for subject in student.enrolled_subjects:
        assignments = Assignment.query.filter_by(subject_id=subject.id).all()
        for a in assignments:
            events.append({
                'id': a.id,
                'title': f"[{subject.code}] {a.title}",
                'start': a.due_date.isoformat(),
                'backgroundColor': '#2E5B27', 
                'borderColor': '#2E5B27',
                'textColor': '#ffffff',
                'url': url_for('student.subject_detail', subject_id=subject.id)
            })
    return jsonify(events)

@student_bp.route('/api/upcoming_events')
def upcoming_events():
    """Returns assignments due in the next 7 days"""
    if not is_student():
        return jsonify([])

    student_id = session.get('user_id')
    student = User.query.get(student_id)
    now = datetime.utcnow()
    one_week_later = now + timedelta(days=7)
    
    upcoming = []
    for subject in student.enrolled_subjects:
        assignments = Assignment.query.filter(
            Assignment.subject_id == subject.id,
            Assignment.due_date >= now,
            Assignment.due_date <= one_week_later
        ).all()
        
        for a in assignments:
            upcoming.append({
                'title': a.title,
                'date': a.due_date.isoformat(),
                'time': a.due_date.strftime('%I:%M %p'),
                'type': 'assignment',
                'icon': 'tasks',
                'description': f"Subject: {subject.name}"
            })
            
    # Sort by date
    upcoming.sort(key=lambda x: x['date'])
    return jsonify(upcoming)

@student_bp.route("/subjects")
def subjects():
    if not is_student():
        return redirect(url_for("auth.login"))

    student = User.query.get(session.get('user_id'))
    enrolled_subjects = student.enrolled_subjects
    
    # Calculate global stats for the bottom of the page
    total_completed = 0
    total_possible = 0
    
    # Add dynamic progress to each subject object for the template
    for s in enrolled_subjects:
        total_assignments = Assignment.query.filter_by(subject_id=s.id).count()
        completed = Submission.query.filter(
            Submission.student_id == student.id,
            Submission.assignment_id.in_([a.id for a in s.assignments])
        ).count()
        
        s.progress_percentage = round((completed / total_assignments * 100), 1) if total_assignments > 0 else 0
        s.teacher_name = s.teacher.name if s.teacher else "Not Assigned"
        
        total_completed += completed
        total_possible += total_assignments

    avg_progress = round((total_completed / total_possible * 100), 1) if total_possible > 0 else 0

    return render_template("student_subjects.html", 
                           subjects=enrolled_subjects,
                           completed_assignments=total_completed,
                           average_progress=avg_progress)

@student_bp.route('/api/subject/<int:subject_id>/info')
def subject_info_api(subject_id):
    """API for the info modal"""
    if not is_student():
        return jsonify({'error': 'Unauthorized'}), 401
        
    subject = Subject.query.get_or_404(subject_id)
    student_id = session.get('user_id')
    
    total_assignments = Assignment.query.filter_by(subject_id=subject.id).count()
    completed = Submission.query.filter_by(student_id=student_id).filter(
        Submission.assignment_id.in_([a.id for a in subject.assignments])
    ).count()

    return jsonify({
        'name': subject.name,
        'code': subject.code,
        'description': subject.description,
        'teacher_name': subject.teacher.name if subject.teacher else "Unassigned",
        'enrolled_count': len(subject.enrolled_students),
        'assignments_count': total_assignments,
        'completed_assignments': completed,
        'pending_assignments': total_assignments - completed,
        'progress_percentage': round((completed/total_assignments*100), 1) if total_assignments > 0 else 0
    })

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
    if not is_student():
        return jsonify({'success': False, 'message': 'Authentication required.'}), 401
    
    query = request.args.get('query', '')
    student_id = session.get('user_id')
    student = User.query.get(student_id)
    
    # Filter by student's form
    student_form = getattr(student, 'form', None)
    
    base_query = Subject.query.filter(Subject.name.ilike(f'%{query}%'))
    
    if student_form:
        base_query = base_query.filter_by(form=student_form)
    
    subjects = base_query.all()
    results = [{
        'id': s.id, 
        'name': f"{s.name} Form {s.form}",  # Show form in name
        'code': s.code,
        'form': s.form
    } for s in subjects]
    
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

@student_bp.route('/api/available_subjects')
def get_available_subjects():
    """Get subjects available for enrollment based on student's form"""
    if not is_student():
        return jsonify({'success': False, 'message': 'Authentication required.'}), 401
    
    student_id = session.get('user_id')
    student = User.query.get(student_id)
    
    # Get student's form
    student_form = getattr(student, 'form', None)
    if not student_form:
        return jsonify({'success': False, 'message': 'Student form not set. Please contact admin.'})
    
    # Get subjects for student's form that they're NOT enrolled in
    enrolled_subject_ids = [s.id for s in student.enrolled_subjects]
    
    available_subjects = Subject.query.filter(
        Subject.form == student_form,
        ~Subject.id.in_(enrolled_subject_ids)
    ).order_by(Subject.name).all()
    
    results = [{
        'id': s.id,
        'name': s.full_name,
        'code': s.code,
        'enrollment_key': s.enrollment_key,
        'description': s.description
    } for s in available_subjects]
    
    return jsonify({'success': True, 'subjects': results, 'form': student_form})