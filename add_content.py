# Updated add_content.py
from app import create_app, db
from app.models import Subject, SubjectContent

app = create_app()

def add_sample_content():
    with app.app_context():
        # Retrieve all subjects from the database
        subjects = Subject.query.all()
        
        if not subjects:
            print("No subjects found. Please run add_subjects.py first.")
            return

        print("Adding sample content to subjects...")
        
        for subject in subjects:
            # Check if the subject already has content
            if not subject.contents.first():
                # Add content specific to form
                for i in range(1, 4):
                    title = f"{subject.name} Form {subject.form} - Lesson {i}"
                    body = f"""
                    This is content for {subject.name} Form {subject.form}, Lesson {i}.
                    
                    Topics covered:
                    - Introduction to Form {subject.form} level concepts
                    - Key principles and theories
                    - Practical applications
                    - Form-specific examples
                    
                    This material is specifically designed for Form {subject.form} students
                    and builds upon knowledge from previous forms.
                    """
                    
                    new_content = SubjectContent(
                        title=title,
                        content_body=body,
                        subject_id=subject.id
                    )
                    db.session.add(new_content)
                    print(f"Adding content to {subject.name} Form {subject.form}")
            else:
                print(f"{subject.name} Form {subject.form} already has content. Skipping.")
        
        db.session.commit()
        print("All sample content added to the database.")

if __name__ == "__main__":
    add_sample_content()