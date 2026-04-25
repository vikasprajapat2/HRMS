from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database import db
from models import Employee, Department, Designation, User, Attendance, Leave, Payroll
from sqlalchemy import func, extract
from datetime import datetime, date, timedelta
import json

def get_analytics_data():
    today = date.today()
    first_day_of_month = today.replace(day=1)
    
    # 1. Monthly Attendance %
    attendance_stats = db.session.query(
        Attendance.status, func.count(Attendance.id)
    ).filter(
        Attendance.date >= first_day_of_month,
        Attendance.date <= today
    ).group_by(Attendance.status).all()
    
    attendance_data = {
        'labels': [],
        'data': []
    }
    for stat in attendance_stats:
        attendance_data['labels'].append(stat[0].title())
        attendance_data['data'].append(stat[1])
        
    # If no data, provide empty structure
    if not attendance_data['labels']:
        attendance_data['labels'] = ['No Data']
        attendance_data['data'] = [1]
        
    # Generate last 6 months labels
    last_6_months = []
    for i in range(5, -1, -1):
        # Subtracting i months from today
        month = today.month - i
        year = today.year
        while month <= 0:
            month += 12
            year -= 1
        month_date = date(year, month, 1)
        last_6_months.append({
            'label': month_date.strftime('%b %Y'),
            'month': month_date.month,
            'year': month_date.year
        })
        
    # 2. Leave Trends (Last 6 months)
    leave_data = {'labels': [m['label'] for m in last_6_months], 'data': [0] * 6}
    for i, m in enumerate(last_6_months):
        start_date = date(m['year'], m['month'], 1)
        # Get next month to find end date
        next_month = m['month'] + 1
        next_year = m['year']
        if next_month > 12:
            next_month = 1
            next_year += 1
        end_date = date(next_year, next_month, 1) - timedelta(days=1)
        leave_count = Leave.query.filter(
            Leave.status == 'approved',
            Leave.start_date <= end_date,
            Leave.end_date >= start_date
        ).count()
        leave_data['data'][i] = leave_count
        
    # 3. Salary Cost (Last 6 months)
    salary_data = {'labels': [m['label'] for m in last_6_months], 'data': [0] * 6}
    for i, m in enumerate(last_6_months):
        month_name = m['label'].split(' ')[0] # e.g. 'Oct' or 'October'
        # In our system, payroll.month might be full name or abbreviation. Let's just sum by year and month.
        # Actually Payroll model stores month as string 'January', 'February' etc.
        full_month_name = date(m['year'], m['month'], 1).strftime('%B')
        total_salary = db.session.query(func.sum(Payroll.net_salary)).filter(
            Payroll.year == m['year'],
            Payroll.month == full_month_name
        ).scalar()
        salary_data['data'][i] = float(total_salary or 0)

    return {
        'attendance': json.dumps(attendance_data),
        'leaves': json.dumps(leave_data),
        'salary': json.dumps(salary_data)
    }

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
    
    analytics = get_analytics_data()
    
    return render_template('admin/dashboard.html', 
                         total_employees=total_employees,
                         total_departments=total_departments,
                         total_users=total_users,
                         today_attendance=today_attendance,
                         role='superadmin',
                         analytics=analytics)

@bp.route('/hr-manager')
@login_required
def hr_dashboard():
    if current_user.role.name not in ['hr', 'superadmin']:
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))
    
    total_employees = Employee.query.count()
    total_departments = Department.query.count()
    pending_leaves = Leave.query.filter_by(status='pending').count()
    
    analytics = get_analytics_data()
    
    return render_template('admin/dashboard.html', 
                         total_employees=total_employees,
                         total_departments=total_departments,
                         pending_leaves=pending_leaves,
                         role='hr',
                         analytics=analytics)


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

@bp.route('/audit-logs')
@login_required
def audit_logs():
    """View system audit logs (superadmin only)."""
    if current_user.role.name != 'superadmin':
        flash('Access denied. Only Super Admin can view audit logs.', 'danger')
        return redirect(url_for('auth.login'))
    
    from models import AuditLog
    
    # Optional filtering
    model_filter = request.args.get('model')
    action_filter = request.args.get('action')
    
    query = AuditLog.query
    if model_filter:
        query = query.filter_by(model=model_filter)
    if action_filter:
        query = query.filter_by(action=action_filter)
        
    logs = query.order_by(AuditLog.created_at.desc()).limit(200).all()
    
    # Parse JSON strings into dictionaries for the template
    for log in logs:
        try:
            log.parsed_old = json.loads(log.old_data) if log.old_data else {}
            log.parsed_new = json.loads(log.new_data) if log.new_data else {}
            
            # Combine keys for easy iteration in the template
            keys = set()
            keys.update(log.parsed_old.keys())
            keys.update(log.parsed_new.keys())
            log.changed_keys = sorted(list(keys))
        except:
            log.parsed_old = {}
            log.parsed_new = {}
            log.changed_keys = []
    
    return render_template('admin/audit_logs.html', logs=logs)