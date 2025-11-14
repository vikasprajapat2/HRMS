from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from database import db
from models import User, Role, AuditLog
from flask_bcrypt import Bcrypt
import secrets
import string
import json

bp = Blueprint('hr', __name__, url_prefix='/hr')
bcrypt = Bcrypt()

# Helpers
def generate_password(length=12):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_unique_hr_id():
    # Simple HR id generator: HR-{random6}
    token = secrets.token_hex(3).upper()
    return f"HR-{token}"

@bp.route('/')
@login_required
def index():
    if current_user.role.name != 'superadmin':
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))

    hr_role = Role.query.filter_by(name='hr').first()
    if not hr_role:
        flash('No HR role found. Please create roles first.', 'warning')
        return redirect(url_for('admin.superadmin_dashboard'))

    hrs = User.query.filter_by(role_id=hr_role.id).all()
    return render_template('admin/hr/index.html', hrs=hrs)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if current_user.role.name != 'superadmin':
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')

        # Ensure hr role exists
        hr_role = Role.query.filter_by(name='hr').first()
        if not hr_role:
            hr_role = Role(name='hr', description='HR role')
            db.session.add(hr_role)
            db.session.commit()

        # Generate credentials
        plain_password = generate_password()
        hashed_password = bcrypt.generate_password_hash(plain_password).decode('utf-8')
        unique_id = generate_unique_hr_id()

        # Create user
        user = User(
            name=name,
            email=email,
            phone=phone,
            password=hashed_password,
            role_id=hr_role.id,
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
                new_data=json.dumps({'name': name, 'email': email, 'phone': phone, 'role': 'hr'}),
                ip_address=request.remote_addr
            )
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f'Failed to write audit log: {e}')

        flash(f'HR user created. Generated password: {plain_password} (show only once)', 'success')
        return redirect(url_for('hr.index'))

    return render_template('admin/hr/create.html')

@bp.route('/<int:user_id>/deactivate', methods=['POST'])
@login_required
def deactivate(user_id):
    if current_user.role.name != 'superadmin':
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.get_or_404(user_id)
    user.status = 'inactive'
    db.session.commit()

    log = AuditLog(
        actor_id=current_user.id,
        action='deactivate',
        model='User',
        record_id=user.id,
        old_data=json.dumps({'status': 'active'}),
        new_data=json.dumps({'status': 'inactive'}),
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()

    flash('HR user deactivated', 'success')
    return redirect(url_for('hr.index'))
