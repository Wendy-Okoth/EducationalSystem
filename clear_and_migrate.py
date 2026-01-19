# clear_and_migrate.py
from app import create_app, db
from app.models import Subject

app = create_app()

def clear_old_subjects():
    """Clear old subjects that don't have form information"""
    with app.app_context():
        print("Clearing old subjects...")
        
        # Delete all existing subjects
        deleted_count = Subject.query.delete()
        db.session.commit()
        
        print(f"✅ Deleted {deleted_count} old subjects")
        print("Now run the new add_subjects.py to create form-based subjects")

if __name__ == "__main__":
    clear_old_subjects()