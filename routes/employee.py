from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database import db
from models import Employee, Department, Designation, Schedule, User, Role
from datetime import datetime
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

bp = Blueprint('employee', __name__, url_prefix='/employee')

@bp.route('/')
@login_required
def index():
    employees = Employee.query.all()
    return render_template('admin/employee/index.html', employees=employees)

def _get_logged_in_employee():
    # Try match by user's email
    if current_user.is_authenticated:
        if getattr(current_user, 'email', None):
            emp = Employee.query.filter_by(email=current_user.email).first()
            if emp:
                return emp
        # If synthetic email pattern was used, extract unique_id before '@'
        if getattr(current_user, 'email', None) and '@' in current_user.email:
            uid = current_user.email.split('@')[0]
            emp = Employee.query.filter_by(unique_id=uid).first()
            if emp:
                return emp
    return None

@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if current_user.role.name != 'employee':
        flash('Only employees can change their password here.', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        current_pwd = request.form.get('current_password')
        new_pwd = request.form.get('new_password')
        confirm_pwd = request.form.get('confirm_password')

        if not bcrypt.check_password_hash(current_user.password, current_pwd):
            flash('Current password is incorrect.', 'danger')
            return render_template('employee/change_password.html')

        if not new_pwd or len(new_pwd) < 6:
            flash('New password must be at least 6 characters.', 'warning')
            return render_template('employee/change_password.html')

        if new_pwd != confirm_pwd:
            flash('New password and confirmation do not match.', 'warning')
            return render_template('employee/change_password.html')

        current_user.password = bcrypt.generate_password_hash(new_pwd).decode('utf-8')
        db.session.commit()
        flash('Password updated successfully.', 'success')
        return redirect(url_for('admin.employee_dashboard'))

    return render_template('employee/change_password.html')

@bp.route('/profile', methods=['GET'])
@login_required
def profile():
    if current_user.role.name != 'employee':
        flash('Only employees can view this page.', 'danger')
        return redirect(url_for('auth.login'))
    employee = _get_logged_in_employee()
    return render_template('employee/profile.html', employee=employee)

@bp.route('/my-attendance', methods=['GET'])
@login_required
def my_attendance():
    if current_user.role.name != 'employee':
        flash('Only employees can view this page.', 'danger')
        return redirect(url_for('auth.login'))
    employee = _get_logged_in_employee()
    records = []
    if employee:
        records = employee.attendances[-30:] if employee.attendances else []
    return render_template('employee/my_attendance.html', records=records)

@bp.route('/apply-leave', methods=['GET', 'POST'])
@login_required
def apply_leave():
    if current_user.role.name != 'employee':
        flash('Only employees can view this page.', 'danger')
        return redirect(url_for('auth.login'))
    employee = _get_logged_in_employee()
    if request.method == 'POST' and employee:
        from models import Leave
        leave = Leave(
            employee_id=employee.id,
            leave_type=request.form.get('leave_type'),
            start_date=datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date(),
            end_date=datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date(),
            reason=request.form.get('reason'),
            status='pending'
        )
        db.session.add(leave)
        db.session.commit()
        flash('Leave request submitted.', 'success')
        return redirect(url_for('employee.apply_leave'))
    return render_template('employee/apply_leave.html')

@bp.route('/my-payroll', methods=['GET'])
@login_required
def my_payroll():
    if current_user.role.name != 'employee':
        flash('Only employees can view this page.', 'danger')
        return redirect(url_for('auth.login'))
    employee = _get_logged_in_employee()
    payrolls = []
    if employee:
        payrolls = employee.payrolls or []
    return render_template('employee/my_payroll.html', payrolls=payrolls)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        employee = Employee(
            firstname=request.form.get('firstname'),
            lastname=request.form.get('lastname'),
            unique_id=request.form.get('unique_id'),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            address=request.form.get('address'),
            dob=datetime.strptime(request.form.get('dob'), '%Y-%m-%d').date() if request.form.get('dob') else None,
            gender=request.form.get('gender'),
            religion=request.form.get('religion'),
            marital=request.form.get('marital'),
            department_id=request.form.get('department_id'),
            designation_id=request.form.get('designation_id'),
            schedule_id=request.form.get('schedule_id'),
            status='active'
        )
        db.session.add(employee)
        db.session.commit()

        # Create or update linked portal user using admin-provided password
        portal_password = request.form.get('portal_password')
        if portal_password and employee.unique_id:
            # Ensure role exists
            employee_role = Role.query.filter_by(name='employee').first()
            if not employee_role:
                employee_role = Role(name='employee', description='Employee self-service')
                db.session.add(employee_role)
                db.session.commit()

            email_for_user = employee.email or f"{employee.unique_id}@employee.local"
            existing_user = User.query.filter_by(email=email_for_user).first()
            if not existing_user:
                user = User(
                    role_id=employee_role.id,
                    name=f"{employee.firstname} {employee.lastname}",
                    email=email_for_user,
                    phone=employee.phone,
                    password=bcrypt.generate_password_hash(portal_password).decode('utf-8'),
                    status='active'
                )
                db.session.add(user)
                db.session.commit()
            else:
                # Update existing user's password and ensure role is employee
                existing_user.password = bcrypt.generate_password_hash(portal_password).decode('utf-8')
                existing_user.role_id = employee_role.id
                existing_user.name = f"{employee.firstname} {employee.lastname}"
                existing_user.phone = employee.phone
                db.session.commit()
        
        flash('Employee created successfully!', 'success')
        return redirect(url_for('employee.index'))
    
    departments = Department.query.all()
    designations = Designation.query.all()
    schedules = Schedule.query.all()
    return render_template('admin/employee/create.html', 
                         departments=departments, 
                         designations=designations,
                         schedules=schedules)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    employee = Employee.query.get_or_404(id)
    
    if request.method == 'POST':
        employee.firstname = request.form.get('firstname')
        employee.lastname = request.form.get('lastname')
        employee.unique_id = request.form.get('unique_id')
        employee.email = request.form.get('email')
        employee.phone = request.form.get('phone')
        employee.address = request.form.get('address')
        if request.form.get('dob'):
            employee.dob = datetime.strptime(request.form.get('dob'), '%Y-%m-%d').date()
        employee.gender = request.form.get('gender')
        employee.religion = request.form.get('religion')
        employee.marital = request.form.get('marital')
        employee.department_id = request.form.get('department_id')
        employee.designation_id = request.form.get('designation_id')
        employee.schedule_id = request.form.get('schedule_id')
        
        db.session.commit()
        flash('Employee updated successfully!', 'success')
        return redirect(url_for('employee.index'))
    
    departments = Department.query.all()
    designations = Designation.query.all()
    schedules = Schedule.query.all()
    return render_template('admin/employee/edit.html', 
                         employee=employee,
                         departments=departments, 
                         designations=designations,
                         schedules=schedules)

@bp.route('/<int:id>/show')
@login_required
def show(id):
    employee = Employee.query.get_or_404(id)
    return render_template('admin/employee/show.html', employee=employee)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    employee = Employee.query.get_or_404(id)
    db.session.delete(employee)
    db.session.commit()
    flash('Employee deleted successfully!', 'success')
    return redirect(url_for('employee.index'))
