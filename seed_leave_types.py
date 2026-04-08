from app import app, db
from models import LeaveType

def seed():
    with app.app_context():
        # This will create any missing tables (like leave_types) without dropping existing ones
        db.create_all()
        
        default_types = [
            {'name': 'annual', 'description': 'Standard Annual Leave', 'days_allowed': 14},
            {'name': 'sick', 'description': 'Medical or Sick Leave', 'days_allowed': 7},
            {'name': 'personal', 'description': 'Personal or Emergency Leave', 'days_allowed': 3},
            {'name': 'unpaid', 'description': 'Unpaid Time Off', 'days_allowed': 0},
            {'name': 'other', 'description': 'Other Leave Type', 'days_allowed': 0}
        ]
        
        for dt in default_types:
            exists = LeaveType.query.filter_by(name=dt['name']).first()
            if not exists:
                lt = LeaveType(**dt)
                db.session.add(lt)
        
        db.session.commit()
        print("Leave types seeded successfully.")

if __name__ == '__main__':
    seed()
