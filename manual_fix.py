# manual_fix.py
from app import create_app
import pymysql

app = create_app()

def manual_fix():
    # Get database configuration from app
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    
    # Parse the URI
    # Format: mysql+pymysql://username:password@host/database
    parts = db_uri.replace('mysql+pymysql://', '').split('@')
    user_pass = parts[0].split(':')
    host_db = parts[1].split('/')
    
    username = user_pass[0]
    password = user_pass[1] if len(user_pass) > 1 else ''
    host = host_db[0]
    database = host_db[1] if len(host_db) > 1 else ''
    
    print(f"Connecting to {database} on {host}...")
    
    # Connect to MySQL
    connection = pymysql.connect(
        host=host,
        user=username,
        password=password,
        database=database,
        cursorclass=pymysql.cursors.DictCursor
    )
    
    try:
        with connection.cursor() as cursor:
            print("\n1. Checking subjects table columns...")
            cursor.execute("DESCRIBE subjects")
            subject_columns = [col['Field'] for col in cursor.fetchall()]
            print(f"Current columns: {subject_columns}")
            
            print("\n2. Checking users table columns...")
            cursor.execute("DESCRIBE users")
            user_columns = [col['Field'] for col in cursor.fetchall()]
            print(f"Current columns: {user_columns}")
            
            print("\n3. Adding form column to users if needed...")
            if 'form' not in user_columns:
                cursor.execute("ALTER TABLE users ADD COLUMN form INTEGER")
                print("Added form column to users")
            else:
                print("Form column already exists in users")
            
            print("\n4. Checking subject constraints...")
            cursor.execute("SHOW INDEX FROM subjects WHERE Key_name = 'code'")
            if cursor.fetchone():
                print("Unique constraint on code already exists")
            else:
                # Make sure all subjects have codes
                cursor.execute("UPDATE subjects SET code = CONCAT('SUB', id) WHERE code IS NULL OR code = ''")
                print("Updated subjects with missing codes")
                
                # Add unique constraint
                cursor.execute("ALTER TABLE subjects ADD UNIQUE (code)")
                print("Added unique constraint on code")
            
            print("\n5. Checking existing subject codes...")
            cursor.execute("SELECT COUNT(*) as total, COUNT(DISTINCT code) as unique_codes FROM subjects")
            counts = cursor.fetchone()
            print(f"Total subjects: {counts['total']}, Unique codes: {counts['unique_codes']}")
            
            if counts['total'] != counts['unique_codes']:
                print("WARNING: Duplicate codes found! Fixing...")
                cursor.execute("""
                    UPDATE subjects s1
                    JOIN (
                        SELECT id, CONCAT(SUBSTRING(name, 1, 3), id, '_', FLOOR(RAND() * 1000)) as new_code
                        FROM subjects
                        WHERE code IN (
                            SELECT code FROM subjects GROUP BY code HAVING COUNT(*) > 1
                        )
                    ) s2 ON s1.id = s2.id
                    SET s1.code = s2.new_code
                """)
                print("Fixed duplicate codes")
        
        connection.commit()
        print("\n✅ Manual fix completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        connection.rollback()
    finally:
        connection.close()

if __name__ == "__main__":
    manual_fix()