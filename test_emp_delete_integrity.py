#!/usr/bin/env python
"""
Test deleting employee EMP001 and check for integrity errors
"""

from app import app, db
from models import Employee, Attendance, Check, Salary

print("="*60)
print("  EMPLOYEE EMP001 DELETE TEST - INTEGRITY CHECK")
print("="*60)

with app.app_context():
    # Find employee with EMP001
    emp = Employee.query.filter_by(unique_id='EMP001').first()
    
    if emp:
        print(f'\nEmployee Found:')
        print(f'  ID: {emp.id}')
        print(f'  Unique ID: {emp.unique_id}')
        print(f'  Name: {emp.firstname} {emp.lastname}')
        print(f'  Email: {emp.email}')
        print(f'  Department: {emp.department.name if emp.department else "N/A"}')
        
        # Check related records
        attendances = Attendance.query.filter_by(employee_id=emp.id).count()
        checks = Check.query.filter_by(employee_id=emp.id).count()
        salary = Salary.query.filter_by(employee_id=emp.id).first()
        
        print(f'\nRelated Records:')
        print(f'  Attendances: {attendances}')
        print(f'  Check-ins/outs: {checks}')
        print(f'  Salary Records: {"Yes" if salary else "No"}')
        
        # Try to delete
        print(f'\nAttempting to DELETE employee EMP001...')
        try:
            emp_id = emp.id
            db.session.delete(emp)
            db.session.commit()
            print(f'✓ Employee deleted successfully!')
            
            # Verify
            check = Employee.query.filter_by(unique_id='EMP001').first()
            if check is None:
                print(f'✓ Verified: Employee EMP001 no longer in database')
                
                # Check if related records still exist
                orphaned_att = Attendance.query.filter_by(employee_id=emp_id).count()
                orphaned_checks = Check.query.filter_by(employee_id=emp_id).count()
                
                print(f'\nOrphaned Records After Deletion:')
                print(f'  Orphaned Attendances: {orphaned_att}')
                print(f'  Orphaned Check Records: {orphaned_checks}')
                
                if orphaned_att > 0 or orphaned_checks > 0:
                    print(f'\n⚠ WARNING: Orphaned records found!')
                    print(f'  Database has records referencing deleted employee.')
                else:
                    print(f'\n✓ No orphaned records - database is clean!')
                
        except Exception as e:
            print(f'✗ ERROR during deletion:')
            print(f'  {type(e).__name__}: {str(e)}')
            print(f'\nThis is an INTEGRITY ERROR - relationships prevent deletion!')
            db.session.rollback()
    else:
        print('Employee EMP001 not found in database')
        print('\nAvailable employees:')
        emps = Employee.query.all()
        for e in emps:
            print(f'  - {e.unique_id or "NO_ID"}: {e.firstname} {e.lastname}')

print("\n" + "="*60)
