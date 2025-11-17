from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from database import db
from models import User, Employee, Role
from flask_bcrypt import Bcrypt
from datetime import datetime

bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = (request.form.get('email') or '').strip()
        password = (request.form.get('password') or '').strip()

        # 1) Standard login by email/password for admin/staff users
        user = User.query.filter_by(email=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')

            if user.role.name == 'superadmin':
                return redirect(url_for('admin.superadmin_dashboard'))
            elif user.role.name == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            elif user.role.name == 'hr':
                return redirect(url_for('admin.hr_dashboard'))
            elif user.role.name == 'payroll':
                return redirect(url_for('admin.payroll_dashboard'))
            elif user.role.name == 'moderator':
                return redirect(url_for('admin.moderator_dashboard'))
            else:
                return redirect(url_for('admin.employee_dashboard'))

        # 2) Employee login: username is Employee ID (unique_id), password is ADMIN-SET user password
        employee = Employee.query.filter_by(unique_id=username).first()
        if employee:
            linked_user = None
            # Prefer employee.email if present
            if employee.email:
                linked_user = User.query.filter_by(email=employee.email).first()
            # Otherwise try conventional synthetic email
            if not linked_user:
                synthetic_email = f"{employee.unique_id}@employee.local"
                linked_user = User.query.filter_by(email=synthetic_email).first()

            if linked_user and bcrypt.check_password_hash(linked_user.password, password):
                # Allow login even if role differs; redirect to employee dashboard
                login_user(linked_user)
                flash('Login successful!', 'success')
                return redirect(url_for('admin.employee_dashboard'))

            flash('Invalid Employee ID or password, or account not set up. Contact admin.', 'danger')
            return render_template('auth/login.html')

        flash('Invalid credentials. Use Email+Password (admins) or EmployeeID+Password.', 'danger')
    
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
            phone=phone,
            role_id=3  # Default role (you may need to adjust this)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        # Add password reset logic here
        flash('Password reset link sent to your email.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot-password.html')
