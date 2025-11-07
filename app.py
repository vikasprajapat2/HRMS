from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from datetime import datetime
import os
from functools import wraps
from database import db
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here-change-in-production')

# Database configuration: prefer MySQL if provided, fallback to SQLite
mysql_user = os.getenv('MYSQL_USER')
mysql_password = os.getenv('MYSQL_PASSWORD')
mysql_host = os.getenv('MYSQL_HOST', '127.0.0.1')
mysql_port = os.getenv('MYSQL_PORT', '3306')
mysql_db = os.getenv('MYSQL_DATABASE')

if mysql_user and mysql_password and mysql_db:
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}?charset=utf8mb4"
    )
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employee_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db.init_app(app)
migrate = Migrate(app, db)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Import models and routes after db initialization
from models import User, Employee, Department, Designation, Schedule, Attendance, Leave, Payroll, Check, Salary, LateTime, OverTime, Role
from routes import auth, admin, employee, department, designation, attendance, leave, payroll, schedule, user

# Register blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(admin.bp)
app.register_blueprint(employee.bp)
app.register_blueprint(department.bp)
app.register_blueprint(designation.bp)
app.register_blueprint(attendance.bp)
app.register_blueprint(leave.bp)
app.register_blueprint(payroll.bp)
app.register_blueprint(schedule.bp)
app.register_blueprint(user.bp)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Role-based access decorators
def superadmin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.name != 'superadmin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.name not in ['admin', 'superadmin']:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def hr_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.name not in ['hr', 'admin', 'superadmin']:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('welcome.html')

@app.context_processor
def inject_user():
    return dict(current_user=current_user)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
