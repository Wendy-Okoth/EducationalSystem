# app/models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from datetime import datetime

# Role constants
class Role:
    STUDENT = "STUDENT"
    TEACHER = "TEACHER"
    ADMIN = "ADMIN"

student_subjects = db.Table('student_subjects',
    db.Column('student_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id'), primary_key=True)
)

# In User class, add this line after the role field:
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default=Role.STUDENT, nullable=False)
    form = db.Column(db.Integer, nullable=True)  
    profile_image = db.Column(db.String(255), nullable=True, default='default.png')

    # Status flags
    is_active = db.Column(db.Boolean, default=False)   # Admin approval
    fees_paid = db.Column(db.Boolean, default=False)   # Only for students
    authorized = db.Column(db.Boolean, default=False)  # Only for teachers
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    subjects = db.relationship("Subject", backref="teacher", lazy=True)

    enrolled_subjects = db.relationship('Subject', secondary=student_subjects, lazy='subquery',
        backref=db.backref('students', lazy=True)
    )


    # Password helpers
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_reset_token(self, expires_sec=1800):  # 30 minutes
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        return s.dumps({"user_id": self.id}, salt="password-reset-salt")

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token, salt="password-reset-salt", max_age=expires_sec)
        except Exception:
            return None
        return User.query.get(data["user_id"])


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# In your existing models.py, update the Subject class:
class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    form = db.Column(db.Integer, nullable=False)  # Add this line - Form 1, 2, 3, or 4
    code = db.Column(db.String(20), unique=True, nullable=False)  # Add this line - e.g., "MATH101"
    description = db.Column(db.Text)
    teacher_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    enrollment_key = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Define the one-to-many relationship to SubjectContent
    contents = db.relationship('SubjectContent', backref='subject', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Subject {self.name} Form {self.form}>'
    
    @property
    def full_name(self):
        return f"{self.name} Form {self.form}"

class SubjectContent(db.Model):
    __tablename__ = 'subject_contents'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    content_body = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)

    def __repr__(self):
        return f'<SubjectContent {self.title}>'

class Material(db.Model):
    __tablename__ = "materials"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class Assignment(db.Model):
    __tablename__ = "assignments"
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # MISSING COLUMN: Add this to store the teacher's uploaded paper
    attachment = db.Column(db.String(255), nullable=True) 

    subject = db.relationship('Subject', backref='assignments', lazy=True)
    teacher = db.relationship('User', backref='assignments', lazy=True)

class Submission(db.Model):
    __tablename__ = "submissions"
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey("assignments.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False) 
    grade = db.Column(db.Float, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    assignment = db.relationship('Assignment', backref=db.backref('submissions', lazy=True))
    student = db.relationship('User', backref=db.backref('submissions', lazy=True))

    @property
    def is_graded(self):
        return self.grade is not None


class Enrollment(db.Model):
    __tablename__ = "enrollments"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='notifications', lazy=True)

class CompletedAssignment(db.Model):
    __tablename__ = 'completed_assignments'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    completion_date = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('User', backref='completed_assignments', lazy=True)
    assignment = db.relationship('Assignment', backref='completions', lazy=True)

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    duration_minutes = db.Column(db.Integer, default=30)
    release_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True) # Added for calendar/deadline locking
    is_published = db.Column(db.Boolean, default=False)
    
    subject = db.relationship('Subject', backref=db.backref('quizzes', lazy=True))
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade='all, delete-orphan')

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), default='MCQ')  # e.g., 'MCQ', 'Short Answer'
    points = db.Column(db.Integer, default=1)
    
    options = db.relationship('Option', backref='question', lazy=True, cascade='all, delete-orphan')

class Option(db.Model):
    __tablename__ = 'options'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    text = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    