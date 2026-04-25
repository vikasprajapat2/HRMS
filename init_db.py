"""
Database initialization script
Run this to create the database tables and insert initial data
"""

from app import app
from database import db
from models import Role, User, Department, Designation, Schedule
from flask_bcrypt import Bcrypt
import os

bcrypt = Bcrypt()

def init_database():
    with app.app_context():
        # Drop all tables and recreate
        print("Creating database tables...")
        db.create_all()
        
        # Create roles
        print("Creating roles...")
        roles_data = [
            {'name': 'superadmin', 'description': 'Super Administrator with full access'},
            {'name': 'hr', 'description': 'HR Manager with HR management access'},
            {'name': 'employee', 'description': 'Employee self-service'},
        ]
        
        for role_data in roles_data:
            role = Role.query.filter_by(name=role_data['name']).first()
            if not role:
                role = Role(**role_data)
                db.session.add(role)
        
        db.session.commit()
        
        # Create default superadmin user
        print("Creating default superadmin user...")
        superadmin_role = Role.query.filter_by(name='superadmin').first()
        
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        
        admin_user = User.query.filter_by(email=admin_email).first()
        if not admin_user:
            admin_user = User(
                role_id=superadmin_role.id,
                name='Super Admin',
                email=admin_email,
                phone='1234567890',
                password=bcrypt.generate_password_hash(admin_password).decode('utf-8'),
                status='active'
            )
            db.session.add(admin_user)
        
        # Create sample departments
        print("Creating sample departments...")
        departments = [
            {'name': 'IT', 'description': 'Information Technology'},
            {'name': 'HR', 'description': 'Human Resources'},
            {'name': 'Finance', 'description': 'Finance Department'},
            {'name': 'Sales', 'description': 'Sales Department'},
        ]
        
        for dept_data in departments:
            dept = Department.query.filter_by(name=dept_data['name']).first()
            if not dept:
                dept = Department(**dept_data)
                db.session.add(dept)
        
        # Create sample designations
        print("Creating sample designations...")
        designations = [
            {'name': 'Manager', 'description': 'Department Manager'},
            {'name': 'Senior Developer', 'description': 'Senior Software Developer'},
            {'name': 'Junior Developer', 'description': 'Junior Software Developer'},
            {'name': 'HR Executive', 'description': 'Human Resources Executive'},
            {'name': 'Accountant', 'description': 'Finance Accountant'},
        ]
        
        for desig_data in designations:
            desig = Designation.query.filter_by(name=desig_data['name']).first()
            if not desig:
                desig = Designation(**desig_data)
                db.session.add(desig)
        
        # Create sample schedules
        print("Creating sample schedules...")
        from datetime import time
        schedules = [
            {'name': 'Day Shift', 'time_in': time(9, 0), 'time_out': time(17, 0), 'grace_period_minutes': 15},
            {'name': 'Night Shift', 'time_in': time(22, 0), 'time_out': time(6, 0), 'grace_period_minutes': 15},
            {'name': 'Flexible Shift (8 Hrs)', 'time_in': None, 'time_out': None, 'is_flexible': True, 'working_hours': 8.0},
        ]
        
        for sched_data in schedules:
            sched = Schedule.query.filter_by(name=sched_data['name']).first()
            if not sched:
                sched = Schedule(**sched_data)
                db.session.add(sched)
        
        db.session.commit()
        
        print("\nDatabase initialized successfully!")
        print("\nDefault Login Credentials:")
        print(f"Email: {admin_email}")
        print(f"Password: {admin_password}")
        print("\nYou can now run the application with: python app.py")

if __name__ == '__main__':
    init_database()
