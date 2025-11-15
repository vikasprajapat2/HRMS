from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from database import db
from models import User, Role, Employee, Attendance, Leave, Payroll, AuditLog
from flask_bcrypt import Bcrypt
import json
from functools import wraps

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

    return render_template('admin/user/dashboard.html', user=user, employee=employee, attendances=attendances, leaves=leaves, payrolls=payrolls)
