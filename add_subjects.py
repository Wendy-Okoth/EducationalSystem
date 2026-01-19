# add_subjects.py - COMPLETELY REPLACE OLD FILE
# add_subjects_fixed.py
from app import create_app, db
from app.models import Subject, User, Role

app = create_app()

def add_subjects_to_db():
    with app.app_context():
        print("Creating or getting admin user...")
        
        # Get admin user without checking form field
        admin_user = db.session.execute(
            db.select(User).filter_by(email="admin@edusystem.com")
        ).scalar_one_or_none()
        
        if not admin_user:
            # Create admin without form field
            admin_user = User(
                name="Admin User",
                email="admin@edusystem.com",
                role=Role.ADMIN,
                is_active=True,
                authorized=True
            )
            admin_user.set_password("admin_password")
            db.session.add(admin_user)
            db.session.commit()
            print(f"Created admin user with ID: {admin_user.id}")
        else:
            print(f"Admin user already exists with ID: {admin_user.id}")

        # Your enrollment keys data
        subjects_data = [
            # Mathematics
            ("Mathematics", 1, "MATH101", "MATH492"),
            ("Mathematics", 2, "MATH201", "MATH817"),
            ("Mathematics", 3, "MATH301", "MATH256"),
            ("Mathematics", 4, "MATH401", "MATH603"),
            
            # English
            ("English", 1, "ENG101", "ENG377"),
            ("English", 2, "ENG201", "ENG914"),
            ("English", 3, "ENG301", "ENG158"),
            ("English", 4, "ENG401", "ENG742"),
            
            # Kiswahili
            ("Kiswahili", 1, "KIS101", "KIS675"),
            ("Kiswahili", 2, "KIS201", "KIS119"),
            ("Kiswahili", 3, "KIS301", "KIS834"),
            ("Kiswahili", 4, "KIS401", "KIS402"),
            
            # Physics
            ("Physics", 1, "PHY101", "PHY528"),
            ("Physics", 2, "PHY201", "PHY163"),
            ("Physics", 3, "PHY301", "PHY905"),
            ("Physics", 4, "PHY401", "PHY381"),
            
            # Biology
            ("Biology", 1, "BIO101", "BIO729"),
            ("Biology", 2, "BIO201", "BIO241"),
            ("Biology", 3, "BIO301", "BIO866"),
            ("Biology", 4, "BIO401", "BIO413"),
            
            # Chemistry
            ("Chemistry", 1, "CHEM101", "CHEM582"),
            ("Chemistry", 2, "CHEM201", "CHEM937"),
            ("Chemistry", 3, "CHEM301", "CHEM104"),
            ("Chemistry", 4, "CHEM401", "CHEM671"),
            
            # CRE
            ("CRE", 1, "CRE101", "CRE315"),
            ("CRE", 2, "CRE201", "CRE842"),
            ("CRE", 3, "CRE301", "CRE297"),
            ("CRE", 4, "CRE401", "CRE750"),
            
            # IRE
            ("IRE", 1, "IRE101", "IRE426"),
            ("IRE", 2, "IRE201", "IRE918"),
            ("IRE", 3, "IRE301", "IRE153"),
            ("IRE", 4, "IRE401", "IRE684"),
            
            # Geography
            ("Geography", 1, "GEO101", "GEO539"),
            ("Geography", 2, "GEO201", "GEO207"),
            ("Geography", 3, "GEO301", "GEO861"),
            ("Geography", 4, "GEO401", "GEO494"),
            
            # History
            ("History", 1, "HIST101", "HIST328"),
            ("History", 2, "HIST201", "HIST715"),
            ("History", 3, "HIST301", "HIST940"),
            ("History", 4, "HIST401", "HIST162"),
            
            # Business Studies
            ("Business Studies", 1, "BUS101", "BUSI683"),
            ("Business Studies", 2, "BUS201", "BUSI249"),
            ("Business Studies", 3, "BUS301", "BUSI801"),
            ("Business Studies", 4, "BUS401", "BUSI437"),
            
            # Computer Studies
            ("Computer Studies", 1, "COMP101", "COMP514"),
            ("Computer Studies", 2, "COMP201", "COMP972"),
            ("Computer Studies", 3, "COMP301", "COMP136"),
            ("Computer Studies", 4, "COMP401", "COMP855"),
            
            # Homescience
            ("Homescience", 1, "HOME101", "HOME361"),
            ("Homescience", 2, "HOME201", "HOME704"),
            ("Homescience", 3, "HOME301", "HOME129"),
            ("Homescience", 4, "HOME401", "HOME598"),
            
            # Agriculture
            ("Agriculture", 1, "AGRI101", "AGRI823"),
            ("Agriculture", 2, "AGRI201", "AGRI416"),
            ("Agriculture", 3, "AGRI301", "AGRI950"),
            ("Agriculture", 4, "AGRI401", "AGRI274"),
            
            # French
            ("French", 1, "FRE101", "FREN631"),
            ("French", 2, "FRE201", "FREN185"),
            ("French", 3, "FRE301", "FREN540"),
            ("French", 4, "FRE401", "FREN927"),
            
            # German
            ("German", 1, "GER101", "GERM308"),
            ("German", 2, "GER201", "GERM762"),
            ("German", 3, "GER301", "GERM421"),
            ("German", 4, "GER401", "GERM189"),
            
            # Music
            ("Music", 1, "MUS101", "MUS847"),
            ("Music", 2, "MUS201", "MUS213"),
            ("Music", 3, "MUS301", "MUS659"),
            ("Music", 4, "MUS401", "MUS394"),
            
            # Art
            ("Art", 1, "ART101", "ART506"),
            ("Art", 2, "ART201", "ART178"),
            ("Art", 3, "ART301", "ART932"),
            ("Art", 4, "ART401", "ART645"),
        ]

        print("\n" + "="*80)
        print("ADDING FORM-BASED SUBJECTS")
        print("="*80)
        
        subjects_added = 0
        subjects_skipped = 0
        
        for name, form, code, enrollment_key in subjects_data:
            # Check if subject already exists by code
            existing = db.session.execute(
                db.select(Subject).filter_by(code=code)
            ).scalar_one_or_none()
            
            if existing:
                print(f"⏭️  SKIPPED: {name} Form {form} ({code}) - Already exists")
                subjects_skipped += 1
                continue
            
            # Create new subject
            new_subject = Subject(
                name=name,
                form=form,
                code=code,
                enrollment_key=enrollment_key,
                teacher_id=admin_user.id,
                description=f"{name} for Form {form} students"
            )
            
            db.session.add(new_subject)
            subjects_added += 1
            print(f"✅ ADDED: {name} Form {form} | Code: {code} | Key: {enrollment_key}")
        
        # Commit all changes
        db.session.commit()
        
        # Summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        total_subjects = db.session.execute(db.select(db.func.count(Subject.id))).scalar()
        print(f"Total subjects in database: {total_subjects}")
        print(f"New subjects added: {subjects_added}")
        print(f"Subjects skipped (already exist): {subjects_skipped}")
        
        # Show by form
        print("\n📊 SUBJECTS BY FORM:")
        for form in [1, 2, 3, 4]:
            count = db.session.execute(
                db.select(db.func.count(Subject.id)).filter_by(form=form)
            ).scalar()
            print(f"  Form {form}: {count} subjects")
        
        # Show enrollment keys
        print("\n📋 ENROLLMENT KEYS:")
        print(f"{'Subject':<20} {'Form':<6} {'Code':<10} {'Enrollment Key':<12}")
        print("-"*80)
        
        subjects = db.session.execute(
            db.select(Subject).order_by(Subject.name, Subject.form)
        ).scalars().all()
        
        for subject in subjects:
            print(f"{subject.name:<20} {subject.form:<6} {subject.code:<10} {subject.enrollment_key:<12}")
        
        print("\n✅ Done! Students can now enroll using these keys.")

if __name__ == "__main__":
    add_subjects_to_db()
           