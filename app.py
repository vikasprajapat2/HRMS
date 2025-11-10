from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from datetime import datetime
import os
import logging
from logging.handlers import RotatingFileHandler
from functools import wraps
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

# Configure logging
logging.basicConfig(level=logging.DEBUG)
handler = RotatingFileHandler('flask.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Load environment variables
load_dotenv()

# Initialize Flask extensions (before creating app)
from database import db
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here-change-in-production')
app.logger.addHandler(handler)  # Add log handler to app
app.logger.setLevel(logging.DEBUG)  # Set log level

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

# Initialize extensions with app
db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)
migrate.init_app(app, db)
login_manager.login_view = 'auth.login'  # Route to the login page

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
    try:
        return db.session.get(User, int(user_id))
    except Exception as e:
        app.logger.error(f'Error loading user {user_id}: {str(e)}')
        return None

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

# Using the app instance configured above. The factory `create_app()` is available
# but the code below initializes and registers blueprints on `app` directly, so
# avoid calling `create_app()` here to prevent import errors from an empty
# `routes.__init__`.
# app = create_app()
 
@app.route('/')
def index():
    return render_template('welcome.html')

@app.context_processor
def inject_user():
    return dict(current_user=current_user)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()  # Roll back db session in case of error
    return render_template('errors/500.html'), 500

# Ensure all tables exist
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
