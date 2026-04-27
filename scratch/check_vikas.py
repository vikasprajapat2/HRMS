from app import app
from database import db
from models import User, Employee
with app.app_context():
    users = User.query.filter(User.name.ilike('%vikas%') | User.email.ilike('%vikas%')).all()
    print('USERS:')
    for u in users:
        print(f'ID: {u.id}, Name: {u.name}, Email: {u.email}, Role ID: {u.role_id}, Status: {u.status}')
    emps = Employee.query.filter(Employee.firstname.ilike('%vikas%') | Employee.email.ilike('%vikas%')).all()
    print('EMPLOYEES:')
    for e in emps:
        print(f'ID: {e.id}, Name: {e.firstname} {e.lastname}, Email: {e.email}, Emp ID: {e.unique_id}, Status: {e.status}')
