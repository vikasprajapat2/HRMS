from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database import db
from models import User, Role, Employee, Attendance, Leave, Payroll
from flask_bcrypt import Bcrypt

bp = Blueprint('user', __name__, url_prefix='/user')
bcrypt = Bcrypt()

@bp.route('/')
@login_required
def index():
    users = User.query.all()
    return render_template('admin/user/index.html', users=users)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
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

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        user.phone = request.form.get('phone')
        user.role_id = request.form.get('role_id')
        user.status = request.form.get('status')
        
        if request.form.get('password'):
            user.password = bcrypt.generate_password_hash(request.form.get('password')).decode('utf-8')
        
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('user.index'))
    
    roles = Role.query.all()
    return render_template('admin/user/edit.html', user=user, roles=roles)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
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

    # Try to find a linked Employee record by email
    try:
        employee = Employee.query.filter_by(email=user.email).first()
    except Exception:
        employee = None

    if employee:
        attendances = Attendance.query.filter_by(employee_id=employee.id).order_by(Attendance.date.desc()).limit(7).all()
        leaves = Leave.query.filter_by(employee_id=employee.id).order_by(Leave.created_at.desc()).limit(5).all()
        payrolls = Payroll.query.filter_by(employee_id=employee.id).order_by(Payroll.year.desc(), Payroll.month.desc()).limit(6).all()

    return render_template('admin/user/dashboard.html', user=user, employee=employee, attendances=attendances, leaves=leaves, payrolls=payrolls)
