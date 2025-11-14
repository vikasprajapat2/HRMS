from flask_login import UserMixin
from datetime import datetime, timedelta
from database import db

class Holiday(db.Model):
    __tablename__ = 'holidays'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.String(50))  # 'government', 'company', etc.
    is_paid = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    users = db.relationship('User', backref='role', lazy=True)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default='active')
    password = db.Column(db.String(255), nullable=False)
    remember_token = db.Column(db.String(100))
    email_verified_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Department(db.Model):
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    employees = db.relationship('Employee', backref='department', lazy=True)

class Designation(db.Model):
    __tablename__ = 'designations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    employees = db.relationship('Employee', backref='designation', lazy=True)

class Schedule(db.Model):
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    time_in = db.Column(db.Time, nullable=False)
    time_out = db.Column(db.Time, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    employees = db.relationship('Employee', backref='schedule', lazy=True)

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    designation_id = db.Column(db.Integer, db.ForeignKey('designations.id'))
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id'))
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    unique_id = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    dob = db.Column(db.Date)
    gender = db.Column(db.String(10))
    religion = db.Column(db.String(50))
    marital = db.Column(db.String(20))
    image = db.Column(db.String(255))  # Store image filename
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    attendances = db.relationship('Attendance', backref='employee', lazy=True, cascade='all, delete-orphan')
    checks = db.relationship('Check', backref='employee', lazy=True, cascade='all, delete-orphan')
    salary = db.relationship('Salary', backref='employee', uselist=False, cascade='all, delete-orphan')
    leaves = db.relationship('Leave', backref='employee', lazy=True, cascade='all, delete-orphan')
    late_times = db.relationship('LateTime', backref='employee', lazy=True, cascade='all, delete-orphan')
    over_times = db.relationship('OverTime', backref='employee', lazy=True, cascade='all, delete-orphan')
    payrolls = db.relationship('Payroll', backref='employee', lazy=True, cascade='all, delete-orphan')

    def generate_attendance(self, start_date, end_date):
        """Generate attendance records for the employee between given dates."""
        current_date = start_date
        while current_date <= end_date:
            # Skip if attendance record already exists
            if Attendance.query.filter_by(employee_id=self.id, date=current_date).first():
                current_date += timedelta(days=1)
                continue

            # Check if it's a holiday
            holiday = Holiday.query.filter_by(date=current_date).first()
            if holiday:
                status = 'holiday'
                description = holiday.name
            # Check if it's a weekend (5=Saturday, 6=Sunday)
            elif current_date.weekday() in [5, 6]:
                status = 'weekend'
                description = 'Weekend'
            else:
                status = 'absent'  # Default to absent, will be updated when employee checks in
                description = None

            # Check if employee is on approved leave
            leave = Leave.query.filter_by(
                employee_id=self.id,
                status='approved'
            ).filter(
                Leave.start_date <= current_date,
                Leave.end_date >= current_date
            ).first()

            if leave:
                status = 'leave'
                description = f"{leave.leave_type} leave"

            # Create attendance record
            attendance = Attendance(
                employee_id=self.id,
                date=current_date,
                status=status,
                description=description
            )
            db.session.add(attendance)
            current_date += timedelta(days=1)
        db.session.commit()

class Attendance(db.Model):
    __tablename__ = 'attendances'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time_in = db.Column(db.Time)
    time_out = db.Column(db.Time)
    status = db.Column(db.String(20))  # present, absent, holiday, weekend
    description = db.Column(db.Text)  # For holiday name or other notes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Check(db.Model):
    __tablename__ = 'checks'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time_in = db.Column(db.Time)
    time_out = db.Column(db.Time)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Leave(db.Model):
    __tablename__ = 'leaves'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    leave_type = db.Column(db.String(50))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Salary(db.Model):
    __tablename__ = 'salaries'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    basic_salary = db.Column(db.Numeric(10, 2), nullable=False)
    house_rent = db.Column(db.Numeric(10, 2), default=0)
    medical = db.Column(db.Numeric(10, 2), default=0)
    transport = db.Column(db.Numeric(10, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LateTime(db.Model):
    __tablename__ = 'late_times'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    minutes = db.Column(db.Integer, nullable=False)
    deduction = db.Column(db.Numeric(10, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class OverTime(db.Model):
    __tablename__ = 'over_times'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    hours = db.Column(db.Numeric(5, 2), nullable=False)
    rate = db.Column(db.Numeric(10, 2), default=0)
    amount = db.Column(db.Numeric(10, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Payroll(db.Model):
    __tablename__ = 'payrolls'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    month = db.Column(db.String(20), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    basic_salary = db.Column(db.Numeric(10, 2), nullable=False)
    allowances = db.Column(db.Numeric(10, 2), default=0)
    overtime_amount = db.Column(db.Numeric(10, 2), default=0)
    deductions = db.Column(db.Numeric(10, 2), default=0)
    net_salary = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
