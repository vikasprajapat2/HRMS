from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required
from database import db
from models import User
from flask_bcrypt import Bcrypt

bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        current_app.logger.debug(f'Login attempt for email={email}, found_user={bool(user)}')

        if user and bcrypt.check_password_hash(user.password, password):
            current_app.logger.debug(f'User authenticated: id={user.id}, role_id={user.role_id}, role_exists={bool(user.role)}')
            login_user(user)
            flash('Login successful!', 'success')
            
            # Redirect based on role
            if user.role.name == 'superadmin':
                return redirect(url_for('admin.superadmin_dashboard'))
            elif user.role.name == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            elif user.role.name == 'hr':
                return redirect(url_for('admin.hr_dashboard'))
            elif user.role.name == 'payroll':
                return redirect(url_for('admin.payroll_dashboard'))
            else:
                return redirect(url_for('admin.moderator_dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    
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
