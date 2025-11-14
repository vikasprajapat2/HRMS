from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from database import db
from models import Employee, Department, Designation, User, Attendance, Leave, Payroll, Role, AuditLog
from sqlalchemy import func
from datetime import datetime
import secrets
import string
import json
from flask_bcrypt import Bcrypt

bp = Blueprint('admin', __name__)
bcrypt = Bcrypt()

@bp.route('/super')
@login_required
def superadmin_dashboard():
    if current_user.role.name != 'superadmin':
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))
    
    total_employees = Employee.query.count()
    total_departments = Department.query.count()
    total_users = User.query.count()
    today_attendance = Attendance.query.filter_by(date=datetime.now().date()).count()
    
    return render_template('admin/dashboard.html', 
                         total_employees=total_employees,
                         total_departments=total_departments,
                         total_users=total_users,
                         today_attendance=today_attendance,
                         role='superadmin')

@bp.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role.name not in ['admin', 'superadmin']:
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))
    
    total_employees = Employee.query.count()
    total_departments = Department.query.count()
    pending_leaves = Leave.query.filter_by(status='pending').count()
    today_attendance = Attendance.query.filter_by(date=datetime.now().date()).count()
    
    return render_template('admin/dashboard.html', 
                         total_employees=total_employees,
                         total_departments=total_departments,
                         pending_leaves=pending_leaves,
                         today_attendance=today_attendance,
                         role='admin')

@bp.route('/hr-manager')
@login_required
def hr_dashboard():
    if current_user.role.name not in ['hr', 'admin', 'superadmin']:
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))
    
    total_employees = Employee.query.count()
    total_departments = Department.query.count()
    pending_leaves = Leave.query.filter_by(status='pending').count()
    
    return render_template('admin/dashboard.html', 
                         total_employees=total_employees,
                         total_departments=total_departments,
                         pending_leaves=pending_leaves,
                         role='hr')

@bp.route('/manager')
@login_required
def payroll_dashboard():
    if current_user.role.name not in ['payroll', 'admin', 'superadmin']:
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))
    
    total_employees = Employee.query.count()
    current_month_payrolls = Payroll.query.filter_by(
        month=datetime.now().strftime('%B'),
        year=datetime.now().year
    ).count()
    
    return render_template('admin/dashboard.html', 
                         total_employees=total_employees,
                         current_month_payrolls=current_month_payrolls,
                         role='payroll')

@bp.route('/moderator')
@login_required
def moderator_dashboard():
    if current_user.role.name not in ['moderator', 'admin', 'superadmin']:
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))
    
    today_attendance = Attendance.query.filter_by(date=datetime.now().date()).count()
    total_employees = Employee.query.count()
    
    return render_template('admin/dashboard.html', 
                         total_employees=total_employees,
                         today_attendance=today_attendance,
                         role='moderator')


@bp.route('/superadmin/create-user-from-employee', methods=['GET', 'POST'])
@login_required
def create_user_from_employee():
    if current_user.role.name != 'superadmin':
        flash('Super Admin access required', 'danger')
        return redirect(url_for('admin.superadmin_dashboard'))
    
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        role_name = request.form.get('role_name')
        
        employee = Employee.query.get_or_404(employee_id)
        
        # Check if user already exists for this employee
        if User.query.filter_by(email=employee.email).first():
            flash('User already exists for this employee email.', 'warning')
            return redirect(url_for('admin.create_user_from_employee'))
        
        # Get or create role
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name, description=f'{role_name} role')
            db.session.add(role)
            db.session.commit()
        
        # Generate secure password
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()"
        plain_password = ''.join(secrets.choice(alphabet) for _ in range(12))
        hashed_password = bcrypt.generate_password_hash(plain_password).decode('utf-8')
        
        # Create user from employee
        user = User(
            name=f'{employee.firstname} {employee.lastname}',
            email=employee.email,
            phone=employee.phone,
            password=hashed_password,
            role_id=role.id,
            status='active'
        )
        db.session.add(user)
        db.session.commit()
        
        # Audit log
        try:
            log = AuditLog(
                actor_id=current_user.id,
                action='create_from_employee',
                model='User',
                record_id=user.id,
                old_data=json.dumps({'employee_id': employee_id}),
                new_data=json.dumps({'user_id': user.id, 'email': user.email, 'role': role_name}),
                ip_address=request.remote_addr
            )
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f'Failed to write audit log: {e}')
        
        # Show credentials
        return render_template('admin/superadmin/user_credentials.html', user=user, employee=employee, password=plain_password, role=role_name)
    
    # Get all employees without user accounts
    employees = db.session.query(Employee).filter(
        ~Employee.email.in_(db.session.query(User.email))
    ).all()
    
    return render_template('admin/superadmin/create_user_from_employee.html', employees=employees)
