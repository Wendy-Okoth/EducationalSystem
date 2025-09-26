from flask import Blueprint, render_template, session, redirect, url_for , request , jsonify , flash
from app.models import User , db , Subject , SubjectContent , Assignment , Quiz, Question, Option
from datetime import datetime

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

    # Corrected line: Fetch all subjects from the database
    subjects = Subject.query.all()

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        subject_id = request.form.get('subject_id')
        due_date_str = request.form.get('due_date')

        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
        except (ValueError, TypeError):
            flash("Invalid date format.", "danger")
            return redirect(url_for('teacher.create_assignment'))

        new_assignment = Assignment(
            title=title,
            content=content,
            due_date=due_date,
            teacher_id=session['user_id'], # Use session user_id
            subject_id=subject_id
        )

        db.session.add(new_assignment)
        db.session.commit()

        flash("Assignment created successfully!", "success")
        return redirect(url_for('teacher.assignments'))

    return render_template('create_assignment.html', subjects=subjects)

@teacher_bp.route('/api/assignments')
def get_teacher_assignments():
    if not is_teacher():
        return jsonify([])
        
    teacher_id = session.get('user_id')
    assignments = Assignment.query.filter_by(teacher_id=teacher_id).all()
    
    assignments_data = [{
        'title': f"Assignment: {a.title}",
        'start': a.due_date.isoformat(),
        'end': a.due_date.isoformat(),
    } for a in assignments]
    
    return jsonify(assignments_data)

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