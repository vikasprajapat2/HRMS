#!/usr/bin/env python
"""
setup_mysql.py - Set up MySQL database from scratch

Usage:
  1. Make sure MySQL server is running
  2. Run: python setup_mysql.py
  3. Follow prompts or set env vars:
     - MYSQL_HOST (default: localhost)
     - MYSQL_USER (default: root)
     - MYSQL_PASSWORD (default: 1234)
     - MYSQL_PORT (default: 3306)
     - MYSQL_DATABASE (default: hrms_db)
"""

import os
import pymysql
from app import app, db
from models import User, Role, Department, Designation, Employee, Schedule, Attendance, Leave, Payroll, Check, Salary, LateTime, OverTime

# Get DB config from environment
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '1234')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
MYSQL_DB = os.getenv('MYSQL_DATABASE', 'hrms_db')

print("=" * 60)
print("MYSQL DATABASE SETUP")
print("=" * 60)
print(f"Host: {MYSQL_HOST}")
print(f"Port: {MYSQL_PORT}")
print(f"User: {MYSQL_USER}")
print(f"Database: {MYSQL_DB}")
print()

# Step 1: Connect to MySQL and create database
print("Step 1: Creating database...")
try:
    conn = pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        port=MYSQL_PORT,
        connect_timeout=5,
        autocommit=True,
    )
    with conn.cursor() as cur:
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}` DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_unicode_ci")
    conn.close()
    print("✓ Database created/verified")
except Exception as e:
    print(f"✗ Error creating database: {e}")
    raise

# Step 2: Create tables
print("\nStep 2: Creating tables...")
try:
    with app.app_context():
        db.create_all()
    print("✓ All tables created")
except Exception as e:
    print(f"✗ Error creating tables: {e}")
    raise

# Step 3: Seed data
print("\nStep 3: Seeding initial data...")
try:
    with app.app_context():
        # Create roles
        roles_data = [
            {'name': 'superadmin', 'description': 'Super Administrator'},
            {'name': 'admin', 'description': 'Administrator'},
            {'name': 'hr', 'description': 'Human Resources'},
            {'name': 'payroll', 'description': 'Payroll Manager'},
            {'name': 'moderator', 'description': 'Moderator'},
        ]
        
        for role_data in roles_data:
            if not Role.query.filter_by(name=role_data['name']).first():
                role = Role(**role_data)
                db.session.add(role)
        
        db.session.commit()
        print("✓ Roles created")
        
        # Create default admin user
        superadmin_role = Role.query.filter_by(name='superadmin').first()
        if not User.query.filter_by(email='admin@example.com').first():
            from flask_bcrypt import Bcrypt
            bcrypt = Bcrypt(app)
            admin = User(
                name='Administrator',
                email='admin@example.com',
                password=bcrypt.generate_password_hash('1234').decode('utf-8'),
                phone='+1-800-000-0000',
                role_id=superadmin_role.id
            )
            db.session.add(admin)
            db.session.commit()
            print("✓ Default admin user created")
            print(f"  Email: admin@example.com")
            print(f"  Password: 1234")
        
        # Create sample departments
        departments = ['IT', 'Sales', 'HR', 'Finance', 'Operations']
        for dept_name in departments:
            if not Department.query.filter_by(name=dept_name).first():
                dept = Department(name=dept_name, description=f'{dept_name} Department')
                db.session.add(dept)
        
        db.session.commit()
        print("✓ Sample departments created")
        
        # Create sample designations
        designations = ['Manager', 'Senior Developer', 'Developer', 'Intern', 'Analyst']
        for desig_name in designations:
            if not Designation.query.filter_by(name=desig_name).first():
                desig = Designation(name=desig_name, description=f'{desig_name} Position')
                db.session.add(desig)
        
        db.session.commit()
        print("✓ Sample designations created")

except Exception as e:
    print(f"✗ Error seeding data: {e}")
    raise

print("\n" + "=" * 60)
print("✓ DATABASE SETUP COMPLETE")
print("=" * 60)
print("\nYour MySQL database is ready!")
print(f"Database: {MYSQL_DB}")
print(f"Admin Email: admin@example.com")
print(f"Admin Password: 1234")
print("\nYou can now run: python app.py")
print("\nTo update DATABASE_URL in your app:")
print(f"DATABASE_URL=mysql+pymysql://{MYSQL_USER}:PASSWORD@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}")
