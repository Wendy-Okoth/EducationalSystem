# check_database.py
from app import create_app, db
from app.models import Subject, User

app = create_app()

def check_database():
    with app.app_context():
        print("Checking database structure...")
        
        # Check subjects table
        print("\n=== SUBJECTS TABLE ===")
        try:
            subjects = Subject.query.first()
            if subjects:
                print(f"Sample subject: {subjects.name}")
                print(f"Has form field: {hasattr(subjects, 'form')}")
                print(f"Has code field: {hasattr(subjects, 'code')}")
                if hasattr(subjects, 'form'):
                    print(f"Form value: {subjects.form}")
                if hasattr(subjects, 'code'):
                    print(f"Code value: {subjects.code}")
            else:
                print("No subjects found")
        except Exception as e:
            print(f"Error checking subjects: {e}")
        
        # Check users table
        print("\n=== USERS TABLE ===")
        try:
            users = User.query.first()
            if users:
                print(f"Sample user: {users.name}")
                print(f"Has form field: {hasattr(users, 'form')}")
                if hasattr(users, 'form'):
                    print(f"Form value: {users.form}")
            else:
                print("No users found")
        except Exception as e:
            print(f"Error checking users: {e}")
        
        print("\n=== DATABASE INFO ===")
        print(f"Database URI: {db.engine.url}")

if __name__ == "__main__":
    check_database()