# cleanup_duplicate_subjects.py
from app import create_app, db
from app.models import Subject

app = create_app()

def cleanup_duplicate_subjects():
    with app.app_context():
        print("Cleaning up duplicate Form 1 subjects...")
        
        # List of subject names
        subject_names = [
            "Mathematics", "English", "Kiswahili", "Physics", "Biology",
            "Chemistry", "CRE", "IRE", "Geography", "History",
            "Business Studies", "Computer Studies", "Homescience", "Agriculture",
            "French", "German", "Music", "Art"
        ]
        
        deleted_count = 0
        
        for name in subject_names:
            # Get all Form 1 subjects with this name
            subjects = db.session.execute(
                db.select(Subject).filter_by(name=name, form=1)
            ).scalars().all()
            
            if len(subjects) > 1:
                # Keep the one with proper code (MATH101 not MAT001)
                # Delete the old ones with codes like MAT001, ENG001, etc.
                for subject in subjects:
                    if subject.code.endswith('001'):
                        print(f"🗑️  Deleting duplicate: {name} Form 1 (Old code: {subject.code})")
                        db.session.delete(subject)
                        deleted_count += 1
        
        db.session.commit()
        
        print(f"\n✅ Deleted {deleted_count} duplicate subjects")
        
        # Show updated counts
        print("\n📊 UPDATED SUBJECTS BY FORM:")
        for form in [1, 2, 3, 4]:
            count = db.session.execute(
                db.select(db.func.count(Subject.id)).filter_by(form=form)
            ).scalar()
            print(f"  Form {form}: {count} subjects")

if __name__ == "__main__":
    cleanup_duplicate_subjects()