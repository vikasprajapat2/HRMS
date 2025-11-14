#!/usr/bin/env python
"""
Test for operational errors - Employee operations with image field
"""

from app import app, db
from models import Employee, Department

print("="*60)
print("  OPERATIONAL ERROR TEST")
print("="*60)

try:
    with app.app_context():
        # Check database
        dept_count = Department.query.count()
        emp_count = Employee.query.count()
        
        print(f"\n✓ Database Connection: OK")
        print(f"✓ Departments in DB: {dept_count}")
        print(f"✓ Employees in DB: {emp_count}")
        
        emp = Employee.query.first()
        if emp:
            print(f"\n✓ Sample Employee Found:")
            print(f"  Name: {emp.firstname} {emp.lastname}")
            print(f"  Email: {emp.email}")
            print(f"  Image: {emp.image or 'None'}")
            print(f"  Department: {emp.department.name if emp.department else 'None'}")
            print(f"  Status: {emp.status}")
        
        print(f"\n✓ NO OPERATIONAL ERRORS!")
        
except Exception as e:
    print(f"\n✗ OPERATIONAL ERROR:")
    print(f"  Type: {type(e).__name__}")
    print(f"  Message: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
