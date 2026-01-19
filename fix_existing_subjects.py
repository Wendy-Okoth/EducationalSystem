# fix_existing_subjects.py
from app import create_app, db
from app.models import Subject
import random
import string

app = create_app()

def fix_existing_subjects():
    with app.app_context():
        print("Fixing existing subjects...")
        
        # Get all subjects that don't have a code or have empty code
        subjects = Subject.query.filter((Subject.code == None) | (Subject.code == '')).all()
        
        if not subjects:
            print("No subjects need fixing.")
            return
        
        print(f"Found {len(subjects)} subjects without proper codes")
        
        # Generate unique codes for each subject
        used_codes = set()
        for subject in subjects:
            # Create a simple code based on subject name
            base_code = subject.name[:3].upper()
            
            # Make it unique by adding numbers
            counter = 1
            new_code = f"{base_code}{counter:03d}"
            while new_code in used_codes:
                counter += 1
                new_code = f"{base_code}{counter:03d}"
            
            # Set form to 1 for all existing subjects
            subject.form = 1
            subject.code = new_code
            used_codes.add(new_code)
            
            print(f"Fixed: {subject.name} -> Code: {new_code}, Form: 1")
        
        db.session.commit()
        print(f"\n✅ Fixed {len(subjects)} subjects")
        print("Now you can run: flask db upgrade")

if __name__ == "__main__":
    fix_existing_subjects()