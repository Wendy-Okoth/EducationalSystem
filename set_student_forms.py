# set_student_forms.py
from app import create_app, db
from app.models import User, Role

app = create_app()

def set_student_forms():
    with app.app_context():
        print("Setting student forms...")
        
        # Get all students
        students = db.session.execute(
            db.select(User).filter_by(role=Role.STUDENT)
        ).scalars().all()
        
        print(f"Found {len(students)} students")
        
        for student in students:
            # Ask for each student's form
            print(f"\nStudent: {student.name} (ID: {student.id})")
            print("Current form:", student.form if student.form else "Not set")
            
            form = input("Enter form (1-4) or press Enter to skip: ")
            if form in ['1', '2', '3', '4']:
                student.form = int(form)
                print(f"✓ Set form to {form}")
            else:
                print("⏭️  Skipped")
        
        db.session.commit()
        print("\n✅ Student forms updated!")

if __name__ == "__main__":
    set_student_forms()