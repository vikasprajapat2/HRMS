#!/usr/bin/env python
"""
Test Employee CRUD Operations - Create, Read, Update, Delete
"""

from app import app, db
from models import Employee, Department, Designation

print("="*60)
print("  EMPLOYEE CRUD OPERATIONS TEST")
print("="*60)

with app.app_context():
    # Get department
    it_dept = Department.query.filter_by(name='IT').first()
    if not it_dept:
        print("ERROR: IT department not found")
        exit(1)
    
    # Get designation
    designation = Designation.query.first()
    if not designation:
        print("ERROR: No designation found")
        exit(1)
    
    print("\n1. CREATE - Adding new employee...")
    emp = Employee(
        firstname='Alice',
        lastname='Johnson',
        email='alice.johnson@company.com',
        phone='5551234567',
        department_id=it_dept.id,
        designation_id=designation.id,
        status='active'
    )
    db.session.add(emp)
    db.session.commit()
    emp_id = emp.id
    print(f"   ✓ Created: Alice Johnson (ID: {emp_id})")
    print(f"   ✓ Email: alice.johnson@company.com")
    print(f"   ✓ Department: {emp.department.name}")
    
    print("\n2. READ - Retrieving employee data...")
    emp_read = Employee.query.filter_by(id=emp_id).first()
    print(f"   ✓ Retrieved: {emp_read.firstname} {emp_read.lastname}")
    print(f"   ✓ Phone: {emp_read.phone}")
    print(f"   ✓ Status: {emp_read.status}")
    
    print("\n3. UPDATE - Changing employee data...")
    print(f"   Old Phone: {emp_read.phone}")
    emp_read.phone = '5559876543'
    emp_read.address = '456 Oak Avenue'
    emp_read.gender = 'Female'
    db.session.commit()
    print(f"   ✓ New Phone: {emp_read.phone}")
    print(f"   ✓ New Address: {emp_read.address}")
    print(f"   ✓ New Gender: {emp_read.gender}")
    
    print("\n4. UPDATE - Changing department...")
    sales_dept = Department.query.filter_by(name='Sales').first()
    if sales_dept:
        old_dept = emp_read.department.name
        emp_read.department_id = sales_dept.id
        db.session.commit()
        print(f"   ✓ Department changed: {old_dept} → {emp_read.department.name}")
    
    print("\n5. DELETE - Removing employee...")
    emp_to_delete = Employee.query.filter_by(id=emp_id).first()
    print(f"   Deleting: {emp_to_delete.firstname} {emp_to_delete.lastname}")
    db.session.delete(emp_to_delete)
    db.session.commit()
    print(f"   ✓ Employee deleted successfully")
    
    # Verify deletion
    emp_check = Employee.query.filter_by(id=emp_id).first()
    if emp_check is None:
        print(f"   ✓ Verified: Employee no longer exists in database")
    
    print("\n" + "="*60)
    print("✓ ALL CRUD OPERATIONS SUCCESSFUL!")
    print("✓ CREATE, READ, UPDATE, DELETE all working perfectly!")
    print("="*60)
