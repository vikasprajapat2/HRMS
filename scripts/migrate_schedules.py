import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import app
from database import db
from sqlalchemy import text

def migrate():
    with app.app_context():
        print("Starting schedule migration...")
        try:
            # Check if columns exist first by querying them
            db.session.execute(text("SELECT is_flexible, working_hours, grace_period_minutes FROM schedules LIMIT 1"))
            print("Columns already exist. Nothing to do.")
        except Exception as e:
            db.session.rollback()
            print("Adding flexible schedule columns...")
            try:
                # SQLite
                db.session.execute(text("ALTER TABLE schedules ADD COLUMN is_flexible BOOLEAN DEFAULT 0"))
                db.session.execute(text("ALTER TABLE schedules ADD COLUMN working_hours NUMERIC(5, 2) DEFAULT 8.0"))
                db.session.execute(text("ALTER TABLE schedules ADD COLUMN grace_period_minutes INTEGER DEFAULT 0"))
                
                # Also we need to make time_in and time_out nullable.
                # SQLite doesn't support ALTER COLUMN, but since it doesn't strictly enforce it unless using strict tables, it's usually fine.
                db.session.commit()
                print("Migration successful.")
            except Exception as e2:
                db.session.rollback()
                print(f"Error during migration: {e2}")
                # Try MySQL syntax if SQLite fails
                try:
                    db.session.execute(text("ALTER TABLE schedules ADD COLUMN is_flexible BOOLEAN DEFAULT 0, ADD COLUMN working_hours NUMERIC(5, 2) DEFAULT 8.0, ADD COLUMN grace_period_minutes INTEGER DEFAULT 0, MODIFY time_in TIME NULL, MODIFY time_out TIME NULL"))
                    db.session.commit()
                    print("MySQL Migration successful.")
                except Exception as e3:
                    db.session.rollback()
                    print(f"MySQL Migration also failed: {e3}")

if __name__ == '__main__':
    migrate()
