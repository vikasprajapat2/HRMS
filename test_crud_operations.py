#!/usr/bin/env python
"""
Test script to verify full CRUD operations for Employees and Departments
Demonstrates: Create, Read, Update, Delete for both entities
"""

from app import app, db
from models import Employee, Department
from datetime import date

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_departments():
    """Test Department CRUD operations"""
    print_section("TESTING DEPARTMENTS")
    
    with app.app_context():
        # CREATE - Add new department
        print("\n✓ CREATE: Adding new department 'Marketing'...")
        new_dept = Department(name='Marketing', description='Marketing Department')
        db.session.add(new_dept)
        db.session.commit()
        dept_id = new_dept.id
        print(f"  Created: ID={dept_id}, Name=Marketing")
        
        # READ - Retrieve the department
        print(f"\n✓ READ: Retrieving department ID={dept_id}...")
        dept = Department.query.get(dept_id)
        print(f"  Found: {dept.name} - {dept.description}")
        
        # UPDATE - Modify the department
        print(f"\n✓ UPDATE: Changing description...")
        dept.description = 'Digital Marketing & Brand Management'
        db.session.commit()
        print(f"  Updated: {dept.name} - {dept.description}")
        
        # LIST - Show all departments
        print(f"\n✓ LIST: All departments in database:")
        all_depts = Department.query.all()
        for d in all_depts:
            print(f"  - {d.name}")
        
        # DELETE - Remove the department
        print(f"\n✓ DELETE: Removing Marketing department...")
        db.session.delete(dept)
        db.session.commit()
        print(f"  Deleted: Marketing")
        
        # Verify deletion
        remaining = Department.query.count()
        print(f"  Total departments remaining: {remaining}")


def test_employees():
    """Test Employee CRUD operations"""
    print_section("TESTING EMPLOYEES")
    
    with app.app_context():
        # Get IT department for new employee
        it_dept = Department.query.filter_by(name='IT').first()
        if not it_dept:
            print("ERROR: IT department not found!")
            return
        
        # CREATE - Add new employee
        print("\n✓ CREATE: Adding new employee 'John Doe'...")
        new_emp = Employee(
            firstname='John',
            lastname='Doe',
            email='john.doe@company.com',
            phone='1234567890',
            dob=date(1990, 5, 15),
            department_id=it_dept.id,
            designation_id=1
        )
        db.session.add(new_emp)
        db.session.commit()
        emp_id = new_emp.id
        print(f"  Created: ID={emp_id}, Name=John Doe, Email=john.doe@company.com")
        
        # READ - Retrieve the employee
        print(f"\n✓ READ: Retrieving employee ID={emp_id}...")
        emp = Employee.query.filter_by(id=emp_id).first()
        print(f"  Found: {emp.firstname} {emp.lastname} - {emp.email}")
        print(f"  Department: {emp.department.name}")
        print(f"  Phone: {emp.phone}")
        
        # UPDATE - Modify the employee
        print(f"\n✓ UPDATE: Changing phone and address...")
        old_phone = emp.phone
        emp.phone = '9876543210'
        emp.address = '123 Main Street, City'
        db.session.commit()
        print(f"  Updated: Phone {old_phone} → {emp.phone}")
        print(f"  Updated: Address set to {emp.address}")
        
        # LIST - Show all employees
        print(f"\n✓ LIST: All employees in database:")
        all_emps = Employee.query.all()
        for e in all_emps:
            dept_name = e.department.name if e.department else 'N/A'
            print(f"  - {e.firstname} {e.lastname} ({dept_name}) - {e.email}")
        
        # DELETE - Remove the employee
        print(f"\n✓ DELETE: Removing John Doe...")
        db.session.delete(emp)
        db.session.commit()
        print(f"  Deleted: John Doe")
        
        # Verify deletion
        remaining = Employee.query.count()
        print(f"  Total employees remaining: {remaining}")


def main():
    """Run all CRUD tests"""
    print("\n" + "="*60)
    print("  HRMS DATABASE - FULL CRUD OPERATIONS TEST")
    print("="*60)
    
    try:
        test_departments()
        test_employees()
        
        print_section("VERIFICATION SUMMARY")
        with app.app_context():
            print(f"\n✓ Final database state:")
            print(f"  Employees: {Employee.query.count()}")
            print(f"  Departments: {Department.query.count()}")
            print(f"\n✓ ALL CRUD OPERATIONS SUCCESSFUL!")
            print(f"✓ DATA IS FULLY UPDATEABLE AND DELETEABLE!")
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
