import sqlite3
import os

def migrate():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'hrms.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns exist
        cursor.execute("PRAGMA table_info(employees)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'aadhar_file' not in columns:
            cursor.execute("ALTER TABLE employees ADD COLUMN aadhar_file VARCHAR(255)")
            print("Added aadhar_file column to employees table.")
        else:
            print("aadhar_file column already exists.")
            
        if 'resume_file' not in columns:
            cursor.execute("ALTER TABLE employees ADD COLUMN resume_file VARCHAR(255)")
            print("Added resume_file column to employees table.")
        else:
            print("resume_file column already exists.")
            
        conn.commit()
        print("Migration completed successfully.")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
