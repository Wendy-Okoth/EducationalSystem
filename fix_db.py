from app import create_app, db

app = create_app()

with app.app_context():
    print("Connecting to database...")
    db.create_all()
    print("Success! All tables (Assignments, Quizzes, etc.) have been created.")