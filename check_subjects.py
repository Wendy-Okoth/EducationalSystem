from app import create_app
from app.models import Subject

# Create the Flask application context
app = create_app()

with app.app_context():
    # Attempt to find a subject with a name containing "History"
    query = "History"
    subjects = Subject.query.filter(Subject.name.ilike(f'%{query}%')).all()
    
    print(f"Searching for subjects with '{query}'...")
    
    if subjects:
        print("Subjects found:")
        for subject in subjects:
            print(f"- ID: {subject.id}, Name: {subject.name}, Enrollment Key: {subject.enrollment_key}")
    else:
        print("No subjects found. The query returned an empty list.")