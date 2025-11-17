"""Script to retrieve superadmin credentials from the database."""
import os
import sys

# Ensure project root is on sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import app
from models import User, Role

with app.app_context():
    # Get superadmin role
    superadmin_role = Role.query.filter_by(name='superadmin').first()
    
    if not superadmin_role:
        print("No superadmin role found in the database.")
    else:
        # Get all users with superadmin role
        superadmins = User.query.filter_by(role_id=superadmin_role.id).all()
        
        if not superadmins:
            print("No superadmin users found in the database.")
        else:
            print(f"Found {len(superadmin(s))} superadmin user(s):\n")
            for user in superadmins:
                print(f"ID: {user.id}")
                print(f"Name: {user.name}")
                print(f"Email: {user.email}")
                print(f"Status: {user.status}")
                print(f"Password Hash: {user.password}")
                print("-" * 50)
