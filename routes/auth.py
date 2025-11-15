from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from database import db
from models import User
from flask_bcrypt import Bcrypt
from models import Role, AuditLog
import secrets, string, json

bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            # deny login if account inactive
            if getattr(user, 'status', 'active') != 'active':
                flash('Account is inactive. Contact administrator.', 'danger')
                return redirect(url_for('auth.login'))

            remember = True if request.form.get('remember') else False
            login_user(user, remember=remember)
            flash('Login successful!', 'success')

            # Redirect based on role
            role_name = user.role.name if getattr(user, 'role', None) else None
            if role_name == 'superadmin':
                return redirect(url_for('admin.superadmin_dashboard'))
            elif role_name == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            elif role_name == 'hr':
                return redirect(url_for('admin.hr_dashboard'))
            elif role_name == 'payroll':
                return redirect(url_for('admin.payroll_dashboard'))
            elif role_name == 'employee':
                return redirect(url_for('user.dashboard'))
            elif role_name == 'moderator':
                return redirect(url_for('admin.moderator_dashboard'))
            else:
                # default to user dashboard for unknown/unspecified roles
                return redirect(url_for('user.dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    # Only allow logged-in superadmin to create new users
    if not current_user.is_authenticated or getattr(current_user, 'role', None) is None or current_user.role.name != 'superadmin':
        flash('Registration is restricted. Only Super Admin can create new users.', 'warning')
        return redirect(url_for('auth.login'))

    roles = Role.query.order_by(Role.name).all()

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        role_id = request.form.get('role_id') or None

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))

        # Generate secure password
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()"
        plain_password = ''.join(secrets.choice(alphabet) for _ in range(12))
        hashed_password = bcrypt.generate_password_hash(plain_password).decode('utf-8')

        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
            phone=phone,
            role_id=int(role_id) if role_id else None,
            status='active'
        )

        db.session.add(new_user)
        db.session.commit()

        # Audit log
        try:
            log = AuditLog(
                actor_id=current_user.id,
                action='create',
                model='User',
                record_id=new_user.id,
                old_data=None,
                new_data=json.dumps({'name': name, 'email': email, 'phone': phone, 'role_id': role_id}),
                ip_address=request.remote_addr
            )
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f'Failed to write audit log: {e}')

        # Show credentials to superadmin once (not saved in plain text)
        return render_template('auth/credentials.html', user=new_user, password=plain_password)

    return render_template('auth/register.html', roles=roles)

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
