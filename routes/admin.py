from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
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


@bp.route('/diag')
@login_required
def diagnostic():
    """Diagnostic endpoint (login required).
    Returns JSON about the current_user and attempts to render the dashboard template.
    Use this after logging in to confirm whether template rendering or role access is causing the white page.
    """
    role_name = current_user.role.name if current_user.role else None
    info = {
        'user_id': current_user.id,
        'user_name': current_user.name,
        'role': role_name,
    }
    try:
        # Try rendering the dashboard with minimal context to detect template errors
        render_template('admin/dashboard.html', role=role_name, total_employees=0, total_departments=0)
        info['render_ok'] = True
    except Exception as e:
        import traceback
        info['render_ok'] = False
        info['error'] = str(e)
        info['trace'] = traceback.format_exc()

    return jsonify(info)
