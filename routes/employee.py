from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database import db
from models import Employee, Department, Designation, Schedule
from datetime import datetime
import os
from werkzeug.utils import secure_filename

bp = Blueprint('employee', __name__, url_prefix='/employee')

# Configuration for file uploads
UPLOAD_FOLDER = 'static/uploads/employees'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_employee_image(file, employee_id):
    """Save employee image and return filename"""
    if file and file.filename and allowed_file(file.filename):
        # Generate unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"emp_{employee_id}.{ext}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save file
        file.save(filepath)
        return filename
    return None

@bp.route('/')
@login_required
def index():
    employees = Employee.query.all()
    return render_template('admin/employee/index.html', employees=employees)

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
            marital=request.form.get('marital'),
            department_id=request.form.get('department_id'),
            designation_id=request.form.get('designation_id'),
            schedule_id=request.form.get('schedule_id'),
            status='active'
        )
        db.session.add(employee)
        db.session.commit()
        
        # Handle image upload
        if 'image' in request.files:
            image_file = request.files['image']
            image_filename = save_employee_image(image_file, employee.id)
            if image_filename:
                employee.image = image_filename
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
        employee.marital = request.form.get('marital')
        employee.department_id = request.form.get('department_id')
        employee.designation_id = request.form.get('designation_id')
        employee.schedule_id = request.form.get('schedule_id')
        
        # Handle image upload
        if 'image' in request.files:
            image_file = request.files['image']
            image_filename = save_employee_image(image_file, employee.id)
            if image_filename:
                employee.image = image_filename
        
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
