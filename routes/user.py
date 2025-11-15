@bp.route('/payroll/<int:id>/download')
@login_required
def download_payslip(id):
    # Placeholder: Download payslip as PDF or CSV
    payroll = Payroll.query.get_or_404(id)
    try:
        employee = Employee.query.filter_by(email=current_user.email).first()
    except Exception:
        employee = None
    if not employee or payroll.employee_id != employee.id:
        flash('You are not authorized to download this payslip.', 'danger')
        return redirect(url_for('user.dashboard'))
    # For now, just return a simple CSV string as attachment
    from flask import Response
    csv = f"Month,Year,Net Salary\n{payroll.month},{payroll.year},{payroll.net_salary}\n"
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-Disposition":f"attachment;filename=payslip_{payroll.month}_{payroll.year}.csv"}
    )
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from database import db
from models import User, Role, Employee, Attendance, Leave, Payroll, AuditLog
from flask_bcrypt import Bcrypt
import json
from functools import wraps
from database import db
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from flask import current_app

bp = Blueprint('user', __name__, url_prefix='/user')
bcrypt = Bcrypt()

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.name not in ['admin', 'superadmin']:
            flash('Admin access required.', 'danger')
            return redirect(url_for('admin.admin_dashboard'))
        return f(*args, **kwargs)
    return decorated

@bp.route('/')
@login_required
@admin_required
def index():
    users = User.query.all()
    return render_template('admin/user/index.html', users=users)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    if request.method == 'POST':
        hashed_password = bcrypt.generate_password_hash(request.form.get('password')).decode('utf-8')
        
        user = User(
            name=request.form.get('name'),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            password=hashed_password,
            role_id=request.form.get('role_id'),
            status='active'
        )
        db.session.add(user)
        db.session.commit()
        
        # Audit log
        try:
            log = AuditLog(
                actor_id=current_user.id,
                action='create',
                model='User',
                record_id=user.id,
                old_data=None,
                new_data=json.dumps({'name': user.name, 'email': user.email, 'role_id': user.role_id}),
                ip_address=request.remote_addr
            )
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f'Failed to write audit log: {e}')
        
        flash('User created successfully!', 'success')
        return redirect(url_for('user.index'))
    
    roles = Role.query.all()
    return render_template('admin/user/create.html', roles=roles)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        old_data = json.dumps({'name': user.name, 'email': user.email, 'role_id': user.role_id, 'status': user.status})
        
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        user.phone = request.form.get('phone')
        user.role_id = request.form.get('role_id')
        user.status = request.form.get('status')
        
        if request.form.get('password'):
            user.password = bcrypt.generate_password_hash(request.form.get('password')).decode('utf-8')
        
        db.session.commit()
        
        # Audit log
        try:
            log = AuditLog(
                actor_id=current_user.id,
                action='update',
                model='User',
                record_id=user.id,
                old_data=old_data,
                new_data=json.dumps({'name': user.name, 'email': user.email, 'role_id': user.role_id, 'status': user.status}),
                ip_address=request.remote_addr
            )
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f'Failed to write audit log: {e}')
        
        flash('User updated successfully!', 'success')
        return redirect(url_for('user.index'))
    
    roles = Role.query.all()
    return render_template('admin/user/edit.html', user=user, roles=roles)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    user = User.query.get_or_404(id)
    
    # Audit log before deletion
    try:
        log = AuditLog(
            actor_id=current_user.id,
            action='delete',
            model='User',
            record_id=user.id,
            old_data=json.dumps({'name': user.name, 'email': user.email, 'role_id': user.role_id}),
            new_data=None,
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f'Failed to write audit log: {e}')
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('user.index'))


@bp.route('/dashboard')
@login_required
def dashboard():
    user = current_user
    employee = None
    attendances = []
    leaves = []
    payrolls = []

    # Try to find a linked Employee record by email
    try:
        employee = Employee.query.filter_by(email=user.email).first()
    except Exception:
        employee = None

    if employee:
        attendances = Attendance.query.filter_by(employee_id=employee.id).order_by(Attendance.date.desc()).limit(7).all()
        leaves = Leave.query.filter_by(employee_id=employee.id).order_by(Leave.created_at.desc()).limit(5).all()
        payrolls = Payroll.query.filter_by(employee_id=employee.id).order_by(Payroll.year.desc(), Payroll.month.desc()).limit(6).all()

        # Compute basic leave balances for display (year-to-date, approved leaves)
        try:
            current_year = datetime.now().year
            # Company defaults
            policy = {
                'annual': 20,
                'sick': 10,
                'casual': 7
            }
            used = {'annual': 0, 'sick': 0, 'casual': 0}
            approved_leaves = Leave.query.filter_by(employee_id=employee.id, status='approved').filter(Leave.start_date >= datetime(current_year, 1, 1).date()).all()
            for al in approved_leaves:
                # count inclusive days
                days = (al.end_date - al.start_date).days + 1
                key = (al.leave_type or '').lower()
                if key in used:
                    used[key] += days

            leave_balance = {k: max(0, policy.get(k, 0) - used.get(k, 0)) for k in policy}
        except Exception:
            leave_balance = {'annual': 0, 'sick': 0, 'casual': 0}
        # Additional summary metrics for dashboard cards (employee-scoped)
        try:
            today = datetime.now().date()
            first_of_month = today.replace(day=1)
            present_days_month = Attendance.query.filter(Attendance.employee_id == employee.id, Attendance.date >= first_of_month).count()
            pending_leaves = Leave.query.filter_by(employee_id=employee.id, status='pending').count()
            approved_leaves_ytd = Leave.query.filter(Leave.employee_id == employee.id, Leave.status == 'approved').filter(Leave.start_date >= datetime(current_year, 1, 1).date()).count()
            payrolls_this_year = Payroll.query.filter_by(employee_id=employee.id, year=current_year).count()
        except Exception:
            present_days_month = 0
            pending_leaves = 0
            approved_leaves_ytd = 0
            payrolls_this_year = 0
    else:
        leave_balance = {'annual': 0, 'sick': 0, 'casual': 0}
        present_days_month = 0
        pending_leaves = 0
        approved_leaves_ytd = 0
        payrolls_this_year = 0

    return render_template('admin/user/dashboard.html', user=user, employee=employee, attendances=attendances, leaves=leaves, payrolls=payrolls, leave_balance=leave_balance, present_days_month=present_days_month, pending_leaves=pending_leaves, approved_leaves_ytd=approved_leaves_ytd, payrolls_this_year=payrolls_this_year)


@bp.route('/leave/apply', methods=['GET', 'POST'])
@login_required
def apply_leave():
    # Allow logged-in employees to apply for leave linked to their Employee record
    user = current_user
    try:
        employee = Employee.query.filter_by(email=user.email).first()
    except Exception:
        employee = None

    if not employee:
        flash('Employee record not found for current user.', 'danger')
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        try:
            start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
            end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
        except Exception:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('user.dashboard'))

        if start_date > end_date:
            flash('Start date cannot be after end date.', 'danger')
            return redirect(url_for('user.dashboard'))

        # Check for overlapping leaves
        existing_leave = Leave.query.filter(
            Leave.employee_id == employee.id,
            Leave.status != 'rejected',
            Leave.start_date <= end_date,
            Leave.end_date >= start_date
        ).first()

        if existing_leave:
            flash('You already have an approved/pending leave in this date range.', 'warning')
            return redirect(url_for('user.dashboard'))

        leave = Leave(
            employee_id=employee.id,
            leave_type=request.form.get('leave_type'),
            start_date=start_date,
            end_date=end_date,
            reason=request.form.get('reason'),
            status='pending'
        )
        db.session.add(leave)
        db.session.commit()

        # Audit log
        try:
            log = AuditLog(
                actor_id=current_user.id,
                action='create',
                model='Leave',
                record_id=leave.id,
                old_data=None,
                new_data=json.dumps({'employee_id': employee.id, 'start_date': str(start_date), 'end_date': str(end_date), 'leave_type': leave.leave_type}),
                ip_address=request.remote_addr
            )
            db.session.add(log)
            db.session.commit()
        except Exception:
            current_app.logger.exception('Failed to write audit log for leave application')

        flash('Leave request submitted successfully!', 'success')
        return redirect(url_for('user.dashboard'))

    # GET -> redirect back to dashboard (form is embedded there)
    return redirect(url_for('user.dashboard'))


@bp.route('/profile')
@login_required
def profile():
    user = current_user
    try:
        employee = Employee.query.filter_by(email=user.email).first()
    except Exception:
        employee = None
    return render_template('admin/user/profile.html', user=user, employee=employee)


@bp.route('/attendance')
@login_required
def attendance_list():
    # Full attendance history for the logged-in employee
    try:
        employee = Employee.query.filter_by(email=current_user.email).first()
    except Exception:
        employee = None

    attendances = []
    if employee:
        attendances = Attendance.query.filter_by(employee_id=employee.id).order_by(Attendance.date.desc()).all()

    return render_template('admin/user/attendance.html', attendances=attendances, employee=employee)


@bp.route('/leaves')
@login_required
def leaves_list():
    try:
        employee = Employee.query.filter_by(email=current_user.email).first()
    except Exception:
        employee = None

    leaves = []
    if employee:
        leaves = Leave.query.filter_by(employee_id=employee.id).order_by(Leave.start_date.desc()).all()

    return render_template('admin/user/leaves.html', leaves=leaves, employee=employee)


@bp.route('/payrolls')
@login_required
def payrolls_list():
    try:
        employee = Employee.query.filter_by(email=current_user.email).first()
    except Exception:
        employee = None

    payrolls = []
    if employee:
        payrolls = Payroll.query.filter_by(employee_id=employee.id).order_by(Payroll.year.desc(), Payroll.month.desc()).all()

    return render_template('admin/user/payrolls.html', payrolls=payrolls, employee=employee)


@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = current_user
    try:
        employee = Employee.query.filter_by(email=user.email).first()
    except Exception:
        employee = None

    if request.method == 'POST':
        user.name = request.form.get('name') or user.name
        user.phone = request.form.get('phone') or user.phone

        # Update employee details if present
        if employee:
            employee.firstname = request.form.get('firstname') or employee.firstname
            employee.lastname = request.form.get('lastname') or employee.lastname
            employee.phone = request.form.get('phone') or employee.phone

        # Handle image upload
        file = request.files.get('image')
        if file and file.filename:
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(current_app.root_path, current_app.config.get('UPLOAD_FOLDER', 'static/uploads'), 'employees')
            os.makedirs(upload_folder, exist_ok=True)
            path = os.path.join(upload_folder, filename)
            file.save(path)
            # store only filename in db
            if employee:
                employee.image = filename

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user.profile'))

    return render_template('admin/user/edit_profile.html', user=user, employee=employee)


@bp.route('/profile/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    user = current_user
    if request.method == 'POST':
        old = request.form.get('old_password')
        new = request.form.get('new_password')
        confirm = request.form.get('confirm_password')

        if not bcrypt.check_password_hash(user.password, old):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('user.change_password'))
        if new != confirm:
            flash('New passwords do not match.', 'danger')
            return redirect(url_for('user.change_password'))

        user.password = bcrypt.generate_password_hash(new).decode('utf-8')
        db.session.commit()
        flash('Password changed successfully.', 'success')
        return redirect(url_for('user.profile'))

    return render_template('admin/user/change_password.html')


@bp.route('/leave/<int:id>/cancel', methods=['POST'])
@login_required
def cancel_leave(id):
    # Allow employees to cancel their own pending leave requests
    leave = Leave.query.get_or_404(id)
    # find employee record for current user
    try:
        employee = Employee.query.filter_by(email=current_user.email).first()
    except Exception:
        employee = None

    if not employee or leave.employee_id != employee.id:
        flash('You are not authorized to cancel this leave.', 'danger')
        return redirect(url_for('user.dashboard'))

    if leave.status != 'pending':
        flash('Only pending leaves can be cancelled.', 'warning')
        return redirect(url_for('user.dashboard'))

    db.session.delete(leave)
    db.session.commit()
    flash('Leave cancelled successfully.', 'success')
    return redirect(url_for('user.dashboard'))
