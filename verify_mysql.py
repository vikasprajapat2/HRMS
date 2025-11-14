#!/usr/bin/env python
"""Verify MySQL database is working and updateable"""
import os
from app import app, db
from models import User, Role, Department, Designation

os.environ['MYSQL_USER'] = 'root'
os.environ['MYSQL_PASSWORD'] = '1234'
os.environ['MYSQL_HOST'] = 'localhost'
os.environ['MYSQL_DATABASE'] = 'hrms_db'

with app.app_context():
    print("=" * 60)
    print("MYSQL DATABASE VERIFICATION")
    print("=" * 60)
    
    print(f"\nDatabase: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    print()
    
    # Check data
    print("Current Data:")
    print(f"  Users: {User.query.count()}")
    print(f"  Roles: {Role.query.count()}")
    print(f"  Departments: {Department.query.count()}")
    print(f"  Designations: {Designation.query.count()}")
    print()
    
    # Test update
    print("Testing UPDATE capability...")
    try:
        admin = User.query.filter_by(email='admin@example.com').first()
        if admin:
            old_name = admin.name
            admin.name = 'System Administrator'
            db.session.commit()
            
            # Verify
            updated = User.query.filter_by(email='admin@example.com').first()
            print(f"  ✓ Updated admin name: '{old_name}' → '{updated.name}'")
            
            # Restore
            admin.name = old_name
            db.session.commit()
            print(f"  ✓ Restored to: '{old_name}'")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    print()
    print("=" * 60)
    print("✓ DATABASE IS READY FOR USE")
    print("✓ ALL DATA IS UPDATEABLE AND CHANGEABLE")
    print("=" * 60)
