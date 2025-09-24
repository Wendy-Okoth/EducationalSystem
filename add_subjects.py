from app import create_app, db
from app.models import Subject, User, Role
from werkzeug.security import generate_password_hash

app = create_app()

def add_subjects_to_db():
    with app.app_context():
        # Step 1: Create or retrieve the admin user within this session
        print("Creating or getting admin user...")
        admin_user = User.query.filter_by(email="admin@edusystem.com").first()
        if not admin_user:
            admin_user = User(
                name="Admin User",
                email="admin@edusystem.com",
                role=Role.ADMIN,
                is_active=True,
                authorized=True
            )
            admin_user.set_password("admin_password")
            db.session.add(admin_user)
            db.session.commit()  # Commit to assign an ID to the user object

        # Step 2: Define all subjects, including the new ones
        subjects_list = [
            ("Mathematics", "MATH101"),
            ("English", "ENG102"),
            ("Kiswahili", "KIS103"),
            ("Physics", "PHY201"),
            ("Biology", "BIO202"),
            ("Chemistry", "CHEM203"),
            ("CRE", "CRE301"),
            ("IRE", "IRE302"),
            ("Geography", "GEO401"),
            ("History", "HIST402"),
            ("Business Studies", "BUSI501"),
            ("Computer Studies", "COMP502"),
            ("Homescience", "HOME601"),
            ("Agriculture", "AGRI602"),
            ("French", "FREN701"),
            ("German", "GERM702"),
            ("Music", "MUS801"),
            ("Art", "ART802")
        ]

        # Step 3: Add subjects to the database
        print("Adding subjects...")
        for name, key in subjects_list:
            # Check if the subject already exists
            subject = Subject.query.filter_by(name=name).first()
            if not subject:
                new_subject = Subject(
                    name=name,
                    enrollment_key=key,
                    teacher_id=admin_user.id  # Use the user ID from the same session
                )
                db.session.add(new_subject)
                print(f"Added {name} with key {key}")
            else:
                print(f"{name} already exists. Skipping.")
        
        db.session.commit()  # Final commit for all new subjects
        print("All subjects added to the database.")

if __name__ == "__main__":
    add_subjects_to_db()