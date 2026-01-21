from flask import Blueprint, render_template, session, redirect, url_for , request , jsonify , flash , current_app
from app.models import User , db , Subject , SubjectContent , Assignment , Quiz, Question, Option
from datetime import datetime
import os
from flask import current_app
from werkzeug.utils import secure_filename
from app import db          

teacher_bp = Blueprint("teacher", __name__, url_prefix="/teacher")

def is_teacher():
    """Helper function to check if the user has a teacher role."""
    return session.get('role') == 'TEACHER'

@teacher_bp.route('/dashboard')
def dashboard():
    if not is_teacher():
        return redirect(url_for('auth.login'))

    teacher_id = session.get('user_id')
    teacher = User.query.get(teacher_id)
    
    # Fetch data specifically for this teacher
    my_subjects = Subject.query.filter_by(teacher_id=teacher_id).all()
    my_assignments = Assignment.query.filter_by(teacher_id=teacher_id).all()
    
    return render_template('teacher_dashboard.html', 
                           teacher=teacher,
                           subjects=my_subjects,
                           subjects_count=len(my_subjects),
                           assignments_count=len(my_assignments),
                           now=datetime.utcnow())

@teacher_bp.route('/subjects')
def subjects():
    if not is_teacher():
        return redirect(url_for("auth.login"))
    
    # Fetch the subjects assigned to this teacher
    teacher_id = session.get("user_id")
    my_subjects = Subject.query.filter_by(teacher_id=teacher_id).all()
    
    return render_template('manage_subjects.html', subjects=my_subjects)


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



@teacher_bp.route('/add_content', methods=['GET', 'POST'])
def add_content():
    if not is_teacher():
        return redirect(url_for('auth.login'))

    teacher_id = session.get('user_id')
    my_subjects = Subject.query.filter_by(teacher_id=teacher_id).all()

    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        title = request.form.get('title')
        content_body = request.form.get('content_body')
        
        # 1. Handle File Upload
        file = request.files.get('resource_file')
        filename = None
        
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            
            # FIX: Point exactly to app/static/uploads (no resources folder)
            # This uses the absolute path of your project
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            
            # Ensure folder exists
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
                
            upload_path = os.path.join(upload_folder, filename)
            file.save(upload_path)

        # 2. Save to Database
        new_content = SubjectContent(
            title=title,
            content_body=content_body,
            subject_id=subject_id,
            file_path=filename 
        )
        
        db.session.add(new_content)
        db.session.commit()
        
        flash("Content & Resource published successfully!", "success")
        return redirect(url_for('teacher.subject_detail', subject_id=subject_id))
    
    return render_template('add_content.html', subjects=my_subjects)

@teacher_bp.route('/assignments')
def assignments():
    if not is_teacher():
        return redirect(url_for('auth.login'))

    teacher = User.query.get(session['user_id'])
    my_assignments = Assignment.query.filter_by(teacher_id=teacher.id).order_by(Assignment.due_date.desc()).all()
    
    return render_template('assignments.html', assignments=my_assignments)

@teacher_bp.route('/create_assignment', methods=['GET', 'POST'])
def create_assignment():
    if not is_teacher():
        return redirect(url_for('auth.login'))

    teacher_id = session.get('user_id')
    subjects = Subject.query.filter_by(teacher_id=teacher_id).all()

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        subject_id = request.form.get('subject_id')
        due_date_str = request.form.get('due_date')

        # Handle File Upload
        file = request.files.get('assignment_file')
        unique_filename = None
        
        if file and file.filename != '':
            original_filename = secure_filename(file.filename)
            # Create a unique filename: timestamp_filename.pdf
            unique_filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{original_filename}"
            
            # Ensure path: app/static/uploads/assignments
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'assignments')
            os.makedirs(upload_folder, exist_ok=True)
            
            file.save(os.path.join(upload_folder, unique_filename))

        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
        except (ValueError, TypeError):
            flash("Invalid date format.", "danger")
            return redirect(url_for('teacher.create_assignment'))

        # Create New Assignment with 'attachment' assigned
        new_assignment = Assignment(
            title=title,
            description=content,
            due_date=due_date,
            teacher_id=teacher_id,
            subject_id=subject_id,
            attachment=unique_filename  # This links the file to the DB record
        )

        db.session.add(new_assignment)
        db.session.commit()

        flash("Assignment posted and added to calendar!", "success")
        return redirect(url_for('teacher.assignments'))

    return render_template('create_assignment.html', subjects=subjects)

@teacher_bp.route('/api/calendar_events')
def calendar_events():
    """API endpoint for FullCalendar to fetch events"""
    if not is_teacher():
        return jsonify([])
        
    teacher_id = session.get('user_id')
    assignments = Assignment.query.filter_by(teacher_id=teacher_id).all()
    quizzes = Quiz.query.join(Subject).filter(Subject.teacher_id == teacher_id).all()
    
    events = []
    
    # Add Assignments
    for a in assignments:
        # Event 1: Start/Posted Date
        events.append({
            'title': f"📢 Posted: {a.title}",
            'start': a.created_at.isoformat(),
            'color': '#15803d', # Dark Green
            'description': 'Assignment made available'
        })
        # Event 2: Deadline
        events.append({
            'title': f"⏰ DUE: {a.title}",
            'start': a.due_date.isoformat(),
            'color': '#92400e', # Light Brown
            'description': 'Submission deadline'
        })

    # Add Quizzes
    for q in quizzes:
        events.append({
            'title': f"📝 Quiz: {q.title}",
            'start': q.release_date.isoformat(),
            'color': '#2563eb' # Blue
        })
    
    return jsonify(events)

@teacher_bp.route('/api/assignments')
def get_teacher_assignments():
    if not is_teacher():
        return jsonify([])
        
    teacher_id = session.get('user_id')
    # Fetch Assignments
    assignments = Assignment.query.filter_by(teacher_id=teacher_id).all()
    # Fetch Quizzes
    quizzes = Quiz.query.join(Subject).filter(Subject.teacher_id == teacher_id).all()
    
    events = []
    
    for a in assignments:
        # 1. When it was made available
        events.append({
            'title': f"📢 Available: {a.title}",
            'start': a.created_at.isoformat(),
            'backgroundColor': '#15803d', # Dark Green
            'allDay': True
        })
        # 2. When it is due
        events.append({
            'title': f"⏰ DUE: {a.title}",
            'start': a.due_date.isoformat(),
            'backgroundColor': '#92400e', # Light Brown
            'allDay': False
        })

    for q in quizzes:
        events.append({
            'title': f"📝 Quiz: {q.title}",
            'start': q.release_date.isoformat(),
            'backgroundColor': '#2563eb', # Blue
        })
    
    return jsonify(events)

@teacher_bp.route('/quizzes/create', methods=['GET', 'POST'])
def create_quiz():
    # Authentication and role checking (assuming 'is_teacher' is implemented)
    if 'user_id' not in session or session.get('role') != 'TEACHER':
        return redirect(url_for('auth.login'))

    teacher_id = session['user_id']
    teacher_subjects = Subject.query.filter_by(teacher_id=teacher_id).all()

    if request.method == 'POST':
        try:
            data = request.json
            
            # 1. Create the Quiz object
            new_quiz = Quiz(
                subject_id=data['subject_id'],
                title=data['title'],
                description=data.get('description', ''),
                duration_minutes=data.get('duration_minutes', 30),
                is_published=data.get('is_published', False)
            )
            db.session.add(new_quiz)
            db.session.flush() # Get the new_quiz.id before committing

            # 2. Add Questions and Options
            for q_data in data.get('questions', []):
                new_question = Question(
                    quiz_id=new_quiz.id,
                    text=q_data['text'],
                    type=q_data.get('type', 'MCQ'),
                    points=q_data.get('points', 1)
                )
                db.session.add(new_question)
                db.session.flush()

                # Add options only for MCQ type
                if new_question.type == 'MCQ':
                    for opt_data in q_data.get('options', []):
                        new_option = Option(
                            question_id=new_question.id,
                            text=opt_data['text'],
                            is_correct=opt_data.get('is_correct', False)
                        )
                        db.session.add(new_option)

            db.session.commit()
            return jsonify({'success': True, 'message': 'Quiz created successfully!', 'quiz_id': new_quiz.id})

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Error creating quiz: {str(e)}'}), 500

    # GET request: render the creation form
    return render_template('create_quiz.html', subjects=teacher_subjects)

@teacher_bp.route('/quizzes')
def list_quizzes():
    # Authentication check...
    if 'user_id' not in session or session.get('role') != 'TEACHER':
        return redirect(url_for('auth.login'))

    # Fetch all quizzes created by the current teacher
    teacher_id = session['user_id']
    quizzes = Quiz.query.join(Subject).filter(Subject.teacher_id == teacher_id).all()
    
    return render_template('list_quizzes.html', quizzes=quizzes)

@teacher_bp.route('/subject/<int:subject_id>')
def subject_detail(subject_id):
    if not is_teacher():
        return redirect(url_for("auth.login"))
    
    subject = Subject.query.get_or_404(subject_id)
    
    # 1. Get all students enrolled
    students = []
    if hasattr(subject, 'students'):
        students = subject.students

    # 2. Get all uploaded content (The fix for your missing visibility)
    from app.models import SubjectContent  # Ensure it is imported
    contents = SubjectContent.query.filter_by(subject_id=subject_id).order_by(SubjectContent.created_at.desc()).all()

    return render_template('teacher_subject_detail.html', 
                           subject=subject, 
                           students=students,
                           contents=contents)

@teacher_bp.route('/edit_content/<int:content_id>', methods=['GET', 'POST'])
def edit_content(content_id):
    if not is_teacher():
        return redirect(url_for("auth.login"))
    
    content = SubjectContent.query.get_or_404(content_id)
    # Get the subject so the template can show "Back to Math" etc.
    subject = Subject.query.get(content.subject_id)
    
    if request.method == 'POST':
        content.title = request.form.get('title')
        content.content_body = request.form.get('content_body')
        
        db.session.commit()
        flash('Content updated successfully!', 'success')
        return redirect(url_for('teacher.subject_detail', subject_id=content.subject_id))
    
    return render_template('edit_content.html', content=content, subject=subject)

@teacher_bp.route('/delete_content/<int:content_id>', methods=['POST'])
def delete_content(content_id):
    if not is_teacher():
        return redirect(url_for("auth.login"))
    
    content = SubjectContent.query.get_or_404(content_id)
    subject_id = content.subject_id
    
    if content.file_path:
        file_path = os.path.join(current_app.root_path, 'static/uploads', content.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
            
    db.session.delete(content)
    db.session.commit()
    flash('Resource deleted permanently.', 'success')
    return redirect(url_for('teacher.subject_detail', subject_id=subject_id))

@teacher_bp.route('/profile/update_image', methods=['POST'])
def update_profile_image():
    if 'profile_image' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('teacher.profile'))
    
    file = request.files['profile_image']
    if file.filename == '':
        return redirect(url_for('teacher.profile'))

    if file:
        filename = secure_filename(f"user_{session.get('user_id')}_{file.filename}")
        
        upload_path = os.path.join(current_app.static_folder, 'uploads', 'profiles')
        os.makedirs(upload_path, exist_ok=True)
        
        file.save(os.path.join(upload_path, filename))
        
        # FIXED: Use 'User' instead of 'Teacher'
        user = User.query.get(session.get('user_id'))
        if user:
            user.profile_image = filename
            db.session.commit()
            
            # Update session so the dashboard reflects the change immediately
            session['profile_image'] = filename
            flash('Profile image updated!', 'success')
        
    return redirect(url_for('teacher.profile'))

@teacher_bp.route('/profile/remove_image', methods=['POST'])
def remove_profile_image():
    user = User.query.get(session.get('user_id'))
    if user and user.profile_image:
        file_path = os.path.join(current_app.static_folder, 'uploads/profiles', user.profile_image)
        if os.path.exists(file_path):
            os.remove(file_path)
        user.profile_image = None
        db.session.commit()
        session.pop('profile_image', None)
        flash('Profile image removed.', 'success')
    return redirect(url_for('teacher.profile'))