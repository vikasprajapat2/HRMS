from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from database import db
from models import User, Role, Employee, Attendance, Leave, Payroll, Notification
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

def superadmin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.name != 'superadmin':
            flash('Superadmin access required.', 'danger')
            return redirect(url_for('admin.admin_dashboard'))
        return f(*args, **kwargs)
    return decorated

@bp.route('/')
@login_required
@superadmin_required
def index():
    # Restrict to superadmin only
    if not current_user.is_authenticated or current_user.role.name != 'superadmin':
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))
    
    # Get all users
    users = User.query.all()
    
    # For each user with employee role, try to find linked employee
    user_employee_map = {}
    for user in users:
        if user.role.name == 'employee':
            # Try to find employee by email or synthetic email
            emp = Employee.query.filter_by(email=user.email).first()
            if not emp and '@' in user.email:
                uid = user.email.split('@')[0]
                emp = Employee.query.filter_by(unique_id=uid).first()
            if emp:
                user_employee_map[user.id] = emp
    
    return render_template('admin/user/index.html', users=users, user_employee_map=user_employee_map)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
@superadmin_required
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
        

        
        flash('User created successfully!', 'success')
        return redirect(url_for('user.index'))
    
    roles = Role.query.all()
    return render_template('admin/user/create.html', roles=roles)

@bp.route('/create-from-employee', methods=['GET', 'POST'])
@login_required
@superadmin_required
def create_from_employee():
    """Create user account from selected employee (superadmin only)."""
    if not current_user.is_authenticated or current_user.role.name != 'superadmin':
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        password = request.form.get('password')
        role_id = request.form.get('role_id')
        
        if not employee_id or not password or not role_id:
            flash('Please fill all required fields', 'danger')
            employees = Employee.query.all()
            roles = Role.query.all()
            return render_template('admin/user/create_from_employee.html', employees=employees, roles=roles)
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            employees = Employee.query.all()
            roles = Role.query.all()
            return render_template('admin/user/create_from_employee.html', employees=employees, roles=roles)
        
        employee = Employee.query.get_or_404(employee_id)
        
        # Check if user already exists
        email_for_user = employee.email or f"{employee.unique_id}@employee.local"
        existing_user = User.query.filter_by(email=email_for_user).first()
        
        if existing_user:
            flash(f'User account already exists for this employee ({existing_user.email})', 'warning')
            return redirect(url_for('user.index'))
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        user = User(
            name=f"{employee.firstname} {employee.lastname}",
            email=email_for_user,
            phone=employee.phone,
            password=hashed_password,
            role_id=role_id,
            status='active'
        )
        db.session.add(user)
        db.session.commit()
        

        
        flash(f'User account created for {employee.firstname} {employee.lastname}!', 'success')
        return redirect(url_for('user.index'))
    
    employees = Employee.query.all()
    roles = Role.query.all()
    return render_template('admin/user/create_from_employee.html', employees=employees, roles=roles)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@superadmin_required
def edit(id):
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':

        
        flash('User updated successfully!', 'success')
        return redirect(url_for('user.index'))
    
    roles = Role.query.all()
    return render_template('admin/user/edit.html', user=user, roles=roles)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@superadmin_required
def delete(id):
    user = User.query.get_or_404(id)
    

    
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
    today_attendance = None

    # Try to find a linked Employee record by email
    try:
        employee = Employee.query.filter_by(email=user.email).first()
    except Exception:
        employee = None

    if employee:
        attendances = Attendance.query.filter_by(employee_id=employee.id).order_by(Attendance.date.desc()).limit(7).all()
        leaves = Leave.query.filter_by(employee_id=employee.id).order_by(Leave.created_at.desc()).limit(5).all()
        payrolls = Payroll.query.filter_by(employee_id=employee.id).order_by(Payroll.year.desc(), Payroll.month.desc()).limit(6).all()
        
        # Get today's attendance for self check-in widget
        today = datetime.now().date()
        today_attendance = Attendance.query.filter_by(employee_id=employee.id, date=today).first()

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
            
            # Check for missed attendance (absent on past days this month)
            missed_attendances = Attendance.query.filter(
                Attendance.employee_id == employee.id,
                Attendance.date >= first_of_month,
                Attendance.date < today,
                Attendance.status == 'absent'
            ).order_by(Attendance.date.desc()).all()
            
        except Exception:
            present_days_month = 0
            pending_leaves = 0
            approved_leaves_ytd = 0
            payrolls_this_year = 0
            missed_attendances = []
    else:
        leave_balance = {'annual': 0, 'sick': 0, 'casual': 0}
        present_days_month = 0
        pending_leaves = 0
        approved_leaves_ytd = 0
        payrolls_this_year = 0
        missed_attendances = []

    return render_template('admin/user/dashboard.html', user=user, employee=employee, attendances=attendances, leaves=leaves, payrolls=payrolls, leave_balance=leave_balance, present_days_month=present_days_month, pending_leaves=pending_leaves, approved_leaves_ytd=approved_leaves_ytd, payrolls_this_year=payrolls_this_year, today_attendance=today_attendance, missed_attendances=missed_attendances)

@bp.route('/self-check', methods=['POST'])
@login_required
def self_check():
    """Endpoint for employees to check themselves in and out."""
    user = current_user
    try:
        employee = Employee.query.filter_by(email=user.email).first()
    except Exception:
        employee = None

    if not employee:
        flash('Employee record not found. Cannot mark attendance.', 'danger')
        return redirect(url_for('user.dashboard'))

    action = request.form.get('action')
    now = datetime.now()
    current_date = now.date()
    current_time = now.time()

    attendance = Attendance.query.filter_by(employee_id=employee.id, date=current_date).first()

    if action == 'in':
        if not attendance:
            attendance = Attendance(
                employee_id=employee.id,
                date=current_date,
                time_in=current_time,
                status='present'
            )
            db.session.add(attendance)
        else:
            attendance.time_in = current_time
            if attendance.status in ['absent', 'weekend', 'leave']:
                attendance.status = 'present'
        flash('Successfully Checked In!', 'success')
    elif action == 'out':
        if attendance:
            attendance.time_out = current_time
            flash('Successfully Checked Out!', 'success')
        else:
            flash('Cannot check out without checking in first.', 'danger')

    db.session.commit()
    return redirect(url_for('user.dashboard'))

@bp.route('/directory')
@login_required
def directory():
    """Company Directory accessible to employees."""
    employees = Employee.query.filter_by(status='active').order_by(Employee.firstname).all()
    return render_template('admin/user/directory.html', employees=employees)

@bp.route('/payslip/<int:id>')
@login_required
def payslip(id):
    """View/Print specific payslip."""
    payroll = Payroll.query.get_or_404(id)
    
    # Ensure they can only view their own payslip (superadmin/hr can view all)
    if current_user.role.name not in ['superadmin', 'hr']:
        try:
            employee = Employee.query.filter_by(email=current_user.email).first()
            if not employee or payroll.employee_id != employee.id:
                flash('Access denied.', 'danger')
                return redirect(url_for('user.dashboard'))
        except Exception:
            flash('Access denied.', 'danger')
            return redirect(url_for('user.dashboard'))
            
    return render_template('admin/user/payslip.html', payroll=payroll)


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




        from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
        from flask_login import login_required, current_user
        from database import db
        from models import User, Role, Employee, Attendance, Leave, Payroll, AuditLog, Notification
        from flask_bcrypt import Bcrypt
        import json
        from functools import wraps
        from database import db
        from datetime import datetime
        import os
        from werkzeug.utils import secure_filename
        from flask import current_app

@bp.route('/profile')
@login_required

        # Place this route after bp is defined
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

        # Handle document uploads
        if employee:
            docs_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'documents')
            os.makedirs(docs_folder, exist_ok=True)
            
            aadhar = request.files.get('aadhar_file')
            if aadhar and aadhar.filename:
                aadhar_filename = secure_filename(f"{employee.unique_id}_aadhar_{aadhar.filename}")
                aadhar.save(os.path.join(docs_folder, aadhar_filename))
                employee.aadhar_file = aadhar_filename
                
            resume = request.files.get('resume_file')
            if resume and resume.filename:
                resume_filename = secure_filename(f"{employee.unique_id}_resume_{resume.filename}")
                resume.save(os.path.join(docs_folder, resume_filename))
                employee.resume_file = resume_filename

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


@bp.route('/notifications/read/<int:id>')
@login_required
def read_notification(id):
    """Mark a notification as read and redirect back."""
    notif = Notification.query.get_or_404(id)
    if notif.user_id == current_user.id:
        notif.is_read = True
        db.session.commit()
    return redirect(request.referrer or url_for('user.dashboard'))

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
