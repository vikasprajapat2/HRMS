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
        status_label = (stat[0].title() if stat[0] else "Unknown")
        attendance_data['labels'].append(status_label)
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
    
    from models import AuditLog, Project, Task, Applicant, Department
    
    # Summary Widgets
    total_employees = Employee.query.count()
    total_departments = Department.query.count()
    total_users = User.query.count()
    today_attendance = Attendance.query.filter_by(date=datetime.now().date()).count()
    
    # New High-Fidelity Data
    recent_activities = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(5).all()
    upcoming_birthdays = Employee.query.filter(
        func.strftime('%m-%d', Employee.dob) >= datetime.now().strftime('%m-%d')
    ).order_by(func.strftime('%m-%d', Employee.dob)).limit(4).all()
    
    recent_attendance_list = Attendance.query.order_by(Attendance.date.desc(), Attendance.created_at.desc()).limit(5).all()
    pending_leaves_list = Leave.query.filter_by(status='pending').limit(5).all()
    
    # Projects & Tasks
    ongoing_projects = Project.query.filter_by(status='ongoing').limit(5).all()
    recent_applicants = Applicant.query.order_by(Applicant.applied_at.desc()).limit(5).all()
    recent_tasks = Task.query.order_by(Task.created_at.desc()).limit(5).all()
    
    # Department Distribution for Bar Chart
    dept_stats = db.session.query(Department.name, func.count(Employee.id)).join(Employee).group_by(Department.name).all()
    dept_distribution = {
        'labels': [s[0] for s in dept_stats],
        'data': [s[1] for s in dept_stats]
    }
    
    analytics = get_analytics_data()
    
    return render_template('admin/dashboard.html', 
                         total_employees=total_employees,
                         total_departments=total_departments,
                         total_users=total_users,
                         today_attendance=today_attendance,
                         recent_activities=recent_activities,
                         upcoming_birthdays=upcoming_birthdays,
                         recent_attendance_list=recent_attendance_list,
                         pending_leaves_list=pending_leaves_list,
                         ongoing_projects=ongoing_projects,
                         recent_applicants=recent_applicants,
                         recent_tasks=recent_tasks,
                         dept_distribution=json.dumps(dept_distribution),
                         role='superadmin',
                         analytics=analytics)

@bp.route('/dashboard')
@login_required
def admin_dashboard():
    if current_user.role.name == 'superadmin':
        return redirect(url_for('admin.superadmin_dashboard'))
    elif current_user.role.name == 'hr':
        return redirect(url_for('admin.hr_dashboard'))
    else:
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))

@bp.route('/hr-manager')
@login_required
def hr_dashboard():
    if current_user.role.name not in ['hr', 'superadmin']:
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))
    
    total_employees = Employee.query.count()
    total_departments = Department.query.count()
    pending_leaves = Leave.query.filter_by(status='pending').count()
    
    # Detailed HR Metrics
    active_employees = Employee.query.filter_by(status='active').count()
    new_hires_this_month = Employee.query.filter(
        Employee.created_at >= datetime.now().replace(day=1)
    ).count()
    
    # Recent Activities
    from models import AuditLog
    recent_activities = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(5).all()
    
    # Birthdays in next 30 days
    today = datetime.now().date()
    upcoming_birthdays = Employee.query.filter(
        func.strftime('%m-%d', Employee.dob) >= today.strftime('%m-%d')
    ).order_by(func.strftime('%m-%d', Employee.dob)).limit(4).all()
    
    recent_attendance_list = Attendance.query.order_by(Attendance.date.desc()).limit(5).all()
    pending_leaves_list = Leave.query.filter_by(status='pending').limit(5).all()
    
    analytics = get_analytics_data()
    
    return render_template('admin/hr_dashboard.html', 
                         total_employees=total_employees,
                         active_employees=active_employees,
                         new_hires_this_month=new_hires_this_month,
                         total_departments=total_departments,
                         pending_leaves=pending_leaves,
                         recent_activities=recent_activities,
                         upcoming_birthdays=upcoming_birthdays,
                         recent_attendance_list=recent_attendance_list,
                         pending_leaves_list=pending_leaves_list,
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