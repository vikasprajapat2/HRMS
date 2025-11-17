from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database import db
from models import Employee, Department, Designation, User, Attendance, Leave, Payroll
from sqlalchemy import func
from datetime import datetime

bp = Blueprint('admin', __name__)

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


@bp.route('/create-user-from-employee')
@login_required
def create_user_from_employee():
    # Provide a simple entry point for superadmins to create portal users from employees.
    # For now redirect to the employee creation form which allows setting portal password.
    if current_user.role.name != 'superadmin':
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))

    return redirect(url_for('employee.create'))


@bp.route('/employee/<int:id>/delete', methods=['POST'])
@login_required
def delete_employee(id):
    """Delete an employee (superadmin only)."""
    if current_user.role.name != 'superadmin':
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))
    
    employee = Employee.query.get_or_404(id)
    db.session.delete(employee)
    db.session.commit()
    flash(f'Employee {employee.firstname} {employee.lastname} deleted successfully!', 'success')
    return redirect(url_for('employee.index'))


@bp.route('/user/<int:id>/delete', methods=['POST'])
@login_required
def delete_user(id):
    """Delete a user (superadmin only)."""
    if current_user.role.name != 'superadmin':
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))
    
    user = User.query.get_or_404(id)
    
    # Prevent superadmin from deleting themselves
    if current_user.id == user.id:
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('user.index'))
    
    # Prevent deletion of superadmin accounts
    if user.role.name == 'superadmin':
        flash('Cannot delete superadmin accounts!', 'danger')
        return redirect(url_for('user.index'))
    
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.name} deleted successfully!', 'success')
    return redirect(url_for('user.index'))