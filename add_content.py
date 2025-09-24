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
                # Add 3 pieces of dummy content for each subject
                for i in range(1, 4):
                    title = f"{subject.name} - Lesson {i}"
                    body = f"This is the content for {subject.name}, covering the basics of Lesson {i}."
                    
                    new_content = SubjectContent(
                        title=title,
                        content_body=body,
                        subject_id=subject.id
                    )
                    db.session.add(new_content)
                    print(f"Adding content '{title}' to {subject.name}")
            else:
                print(f"{subject.name} already has content. Skipping.")
        
        db.session.commit()
        print("All sample content added to the database.")

if __name__ == "__main__":
    add_sample_content()