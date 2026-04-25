import sys, os
# ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import app
from database import db
from models import Role, User

def migrate():
    with app.app_context():
        print("Starting role migration...")
        
        superadmin_role = Role.query.filter_by(name='superadmin').first()
        hr_role = Role.query.filter_by(name='hr').first()
        
        if not superadmin_role or not hr_role:
            print("Required roles 'superadmin' and 'hr' not found. Run init_db.py first or ensure they exist.")
            return

        roles_to_migrate = {
            'admin': superadmin_role,
            'payroll': hr_role,
            'moderator': hr_role
        }

        users_migrated = 0
        for old_role_name, new_role in roles_to_migrate.items():
            old_role = Role.query.filter_by(name=old_role_name).first()
            if old_role:
                users = User.query.filter_by(role_id=old_role.id).all()
                for user in users:
                    print(f"Migrating user {user.email} from {old_role_name} to {new_role.name}")
                    user.role_id = new_role.id
                    users_migrated += 1
                
                # Delete the old role since it's no longer used
                print(f"Deleting deprecated role: {old_role_name}")
                db.session.delete(old_role)
                
        db.session.commit()
        print(f"Migration complete. {users_migrated} users updated.")

if __name__ == '__main__':
    migrate()
