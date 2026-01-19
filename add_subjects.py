from app import create_app, db
from app.models import Subject, User

app = create_app()

def add_subjects_to_db():
    with app.app_context():
        # Finalized Teacher-Subject Mapping
        teachers_mapping = {
            "agnesmumbua@kasaraniacademy.ac.ke": ("Agnes Mumbua", [("French", 1), ("French", 2), ("French", 3), ("French", 4)]),
            "njokinjeri@kasaraniacademy.ac.ke": ("Njoki Njeri", [("German", 1), ("German", 2), ("German", 3), ("German", 4)]),
            "justinkaranja@kasaraniacademy.ac.ke": ("Justin Karanja", [("Art", 1), ("Art", 2), ("Art", 3), ("Art", 4)]),
            "mosesmbugua@kasaraniacademy.ac.ke": ("Moses Mbugua", [("Music", 1), ("Music", 2), ("Music", 3), ("Music", 4)]),
            "titusmwiti@kasaraniacademy.ac.ke": ("Titus Mwiti", [("Mathematics", 1), ("Mathematics", 3), ("Physics", 3), ("Physics", 4), ("Chemistry", 3)]),
            "brightonnamai@kasaraniacademy.ac.ke": ("Brighton Namai", [("Chemistry", 1), ("Chemistry", 2), ("Chemistry", 4), ("Biology", 1), ("Biology", 2)]),
            "sarahamboka@kasaraniacademy.ac.ke": ("Sarah Amboka", [("Biology", 3), ("Biology", 4), ("Geography", 1), ("Geography", 2)]),
            "doreenoduor@kasaraniacademy.ac.ke": ("Doreen Oduor", [("CRE", 3), ("CRE", 4), ("History", 3), ("History", 4)]),
            "joycewamalwa@kasaraniacademy.ac.ke": ("Joyce Wamalwa", [("Mathematics", 2), ("Mathematics", 4), ("CRE", 1)]),
            "aggreysakwa@kasaraniacademy.ac.ke": ("Aggrey Sakwa", [("Geography", 3), ("Geography", 4), ("CRE", 2), ("Kiswahili", 4)]),
            "mariammwale@kasaraniacademy.ac.ke": ("Mariam Mwale", [("IRE", 1), ("IRE", 2), ("IRE", 3), ("IRE", 4), ("Kiswahili", 3)]),
            "georgebarasa@kasaraniacademy.ac.ke": ("George Barasa", [("Business Studies", 3), ("Business Studies", 4), ("Computer Studies", 3), ("Computer Studies", 4)]),
            "susanwanjiku@kasaraniacademy.ac.ke": ("Susan Wanjiku", [("English", 1), ("English", 2), ("English", 3), ("English", 4)]),
            "jameskituzi@kasaraniacademy.ac.ke": ("James Kituzi", [("Homescience", 1), ("Homescience", 2), ("Homescience", 3), ("Homescience", 4)]),
            "calebkule@kasaraniacademy.ac.ke": ("Caleb Kule", [("Agriculture", 1), ("Agriculture", 2), ("Agriculture", 3), ("Agriculture", 4)]),
            "phoebekerubo@kasaraniacademy.ac.ke": ("Phoebe Kerubo", [("History", 1), ("History", 2)]),
            "paulnjuguna@kasaraniacademy.ac.ke": ("Paul Njuguna", [
                ("Physics", 1), ("Physics", 2), ("Kiswahili", 1), ("Kiswahili", 2),
                ("Business Studies", 1), ("Business Studies", 2), ("Computer Studies", 1), ("Computer Studies", 2),
            ]),
        }

        # Subject Raw Data (Code and Enrollment Keys)
        subjects_raw = [
            ("Mathematics", 1, "MATH101", "MATH492"), ("Mathematics", 2, "MATH201", "MATH817"), ("Mathematics", 3, "MATH301", "MATH256"), ("Mathematics", 4, "MATH401", "MATH603"),
            ("English", 1, "ENG101", "ENG377"), ("English", 2, "ENG201", "ENG914"), ("English", 3, "ENG301", "ENG158"), ("English", 4, "ENG401", "ENG742"),
            ("Kiswahili", 1, "KIS101", "KIS675"), ("Kiswahili", 2, "KIS201", "KIS119"), ("Kiswahili", 3, "KIS301", "KIS834"), ("Kiswahili", 4, "KIS401", "KIS402"),
            ("Physics", 1, "PHY101", "PHY528"), ("Physics", 2, "PHY201", "PHY163"), ("Physics", 3, "PHY301", "PHY905"), ("Physics", 4, "PHY401", "PHY381"),
            ("Biology", 1, "BIO101", "BIO729"), ("Biology", 2, "BIO201", "BIO241"), ("Biology", 3, "BIO301", "BIO866"), ("Biology", 4, "BIO401", "BIO413"),
            ("Chemistry", 1, "CHEM101", "CHEM582"), ("Chemistry", 2, "CHEM201", "CHEM937"), ("Chemistry", 3, "CHEM301", "CHEM104"), ("Chemistry", 4, "CHEM401", "CHEM671"),
            ("CRE", 1, "CRE101", "CRE315"), ("CRE", 2, "CRE201", "CRE842"), ("CRE", 3, "CRE301", "CRE297"), ("CRE", 4, "CRE401", "CRE750"),
            ("IRE", 1, "IRE101", "IRE426"), ("IRE", 2, "IRE201", "IRE918"), ("IRE", 3, "IRE301", "IRE153"), ("IRE", 4, "IRE401", "IRE684"),
            ("Geography", 1, "GEO101", "GEO539"), ("Geography", 2, "GEO201", "GEO207"), ("Geography", 3, "GEO301", "GEO861"), ("Geography", 4, "GEO401", "GEO494"),
            ("History", 1, "HIST101", "HIST328"), ("History", 2, "HIST201", "HIST715"), ("History", 3, "HIST301", "HIST940"), ("History", 4, "HIST401", "HIST162"),
            ("Business Studies", 1, "BUS101", "BUSI683"), ("Business Studies", 2, "BUS201", "BUSI249"), ("Business Studies", 3, "BUS301", "BUSI801"), ("Business Studies", 4, "BUS401", "BUSI437"),
            ("Computer Studies", 1, "COMP101", "COMP514"), ("Computer Studies", 2, "COMP201", "COMP972"), ("Computer Studies", 3, "COMP301", "COMP136"), ("Computer Studies", 4, "COMP401", "COMP855"),
            ("Homescience", 1, "HOME101", "HOME361"), ("Homescience", 2, "HOME201", "HOME704"), ("Homescience", 3, "HOME301", "HOME129"), ("Homescience", 4, "HOME401", "HOME598"),
            ("Agriculture", 1, "AGRI101", "AGRI823"), ("Agriculture", 2, "AGRI201", "AGRI416"), ("Agriculture", 3, "AGRI301", "AGRI950"), ("Agriculture", 4, "AGRI401", "AGRI274"),
            ("French", 1, "FRE101", "FREN631"), ("French", 2, "FRE201", "FREN185"), ("French", 3, "FRE301", "FREN540"), ("French", 4, "FRE401", "FREN927"),
            ("German", 1, "GER101", "GERM308"), ("German", 2, "GER201", "GERM762"), ("German", 3, "GER301", "GERM421"), ("German", 4, "GER401", "GERM189"),
            ("Music", 1, "MUS101", "MUS847"), ("Music", 2, "MUS201", "MUS213"), ("Music", 3, "MUS301", "MUS659"), ("Music", 4, "MUS401", "MUS394"),
            ("Art", 1, "ART101", "ART506"), ("Art", 2, "ART201", "ART178"), ("Art", 3, "ART301", "ART932"), ("Art", 4, "ART401", "ART645"),
        ]

        print("--- Starting Subject Assignment ---")
        
        # Cache teachers to avoid multiple DB lookups
        email_to_id = {}
        for email in teachers_mapping.keys():
            user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
            if user:
                email_to_id[email] = user.id
            else:
                print(f"⚠️  WARNING: Teacher account not found for {email}. Please create it first.")

        for name, form, code, enrollment_key in subjects_raw:
            # Find which teacher is assigned to this (Name, Form)
            target_teacher_id = None
            teacher_name_display = "Unknown"

            for email, info in teachers_mapping.items():
                if (name, form) in info[1]:
                    target_teacher_id = email_to_id.get(email)
                    teacher_name_display = info[0]
                    break
            
            if not target_teacher_id:
                print(f"⏭️  SKIPPING {name} Form {form}: No existing teacher ID found.")
                continue

            # Update or Create Subject
            subject = db.session.execute(db.select(Subject).filter_by(code=code)).scalar_one_or_none()
            if subject:
                subject.teacher_id = target_teacher_id
                subject.name = name
                subject.form = form
                print(f"🔄 UPDATED: {name} Form {form} -> {teacher_name_display}")
            else:
                new_sub = Subject(
                    name=name, form=form, code=code,
                    enrollment_key=enrollment_key, teacher_id=target_teacher_id,
                    description=f"{name} for Form {form}"
                )
                db.session.add(new_sub)
                print(f"✅ CREATED: {name} Form {form} -> {teacher_name_display}")

        db.session.commit()
        print("--- Assignment Complete ---")

if __name__ == "__main__":
    add_subjects_to_db()
           