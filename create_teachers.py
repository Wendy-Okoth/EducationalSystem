from app import create_app, db
from app.models import User, Role
import random

app = create_app()

def bulk_create_teachers():
    # Teacher Data
    teachers_data = [
        ("Agnes Mumbua", "agnesmumbua@kasaraniacademy.ac.ke"),
        ("Njoki Njeri", "njokinjeri@kasaraniacademy.ac.ke"),
        ("Justin Karanja", "justinkaranja@kasaraniacademy.ac.ke"),
        ("Moses Mbugua", "mosesmbugua@kasaraniacademy.ac.ke"),
        ("Titus Mwiti", "titusmwiti@kasaraniacademy.ac.ke"),
        ("Brighton Namai", "brightonnamai@kasaraniacademy.ac.ke"),
        ("Sarah Amboka", "sarahamboka@kasaraniacademy.ac.ke"),
        ("Doreen Oduor", "doreenoduor@kasaraniacademy.ac.ke"),
        ("Joyce Wamalwa", "joycewamalwa@kasaraniacademy.ac.ke"),
        ("Aggrey Sakwa", "aggreysakwa@kasaraniacademy.ac.ke"),
        ("Mariam Mwale", "mariammwale@kasaraniacademy.ac.ke"),
        ("George Barasa", "georgebarasa@kasaraniacademy.ac.ke"),
        ("Susan Wanjiku", "susanwanjiku@kasaraniacademy.ac.ke"),
        ("James Kituzi", "jameskituzi@kasaraniacademy.ac.ke"),
        ("Caleb Kule", "calebkule@kasaraniacademy.ac.ke"),
        ("Phoebe Kerubo", "phoebekerubo@kasaraniacademy.ac.ke"),
        ("Paul Njuguna", "paulnjuguna@kasaraniacademy.ac.ke")
    ]

    # Password components
    cities = ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret", "Thika", "Malindi", "Kitale", "Garissa", "Kakamega"]
    symbols = ["!", "@", "#", "$", "&"]

    with app.app_context():
        print(f"{'NAME':<20} | {'EMAIL':<40} | {'PASSWORD'}")
        print("-" * 85)

        for name, email in teachers_data:
            # Check if user already exists
            user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
            
            if not user:
                # Generate unique password: e.g., "1Nairobi#"
                rand_num = random.randint(1, 9)
                rand_city = random.choice(cities)
                rand_sym = random.choice(symbols)
                raw_password = f"{rand_num}{rand_city}{rand_sym}"

                new_teacher = User(
                    name=name,
                    email=email,
                    role="TEACHER",  # Matches your login check
                    is_active=True,  # Bypasses the "account not active" check in login()
                    authorized=True  # Specific for your teacher model
                )
                new_teacher.set_password(raw_password)
                db.session.add(new_teacher)
                
                print(f"{name:<20} | {email:<40} | {raw_password}")
            else:
                print(f"{name:<20} | {email:<40} | ALREADY EXISTS")

        db.session.commit()
        print("\n--- Teacher Accounts Created Successfully ---")
        print("You can now log in with these credentials.")

if __name__ == "__main__":
    bulk_create_teachers()