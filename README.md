# Employee Management System - Python Flask Edition

This is a Python Flask conversion of the Laravel Employee Management System with HTML, CSS, and Bootstrap 5.

## Features

- **User Authentication**: Multi-role authentication system (Superadmin, Admin, HR, Payroll Manager, Moderator)
- **Employee Management**: Create, edit, view, and manage employee profiles
- **Department & Designation Management**: Organize employees by departments and designations
- **Attendance System**: Track daily attendance with check-in/check-out functionality
- **Leave Management**: Handle employee leave requests and approvals
- **Payroll System**: Calculate and manage employee payroll
- **Schedule Management**: Define working hours and schedules
- **User Management**: Manage system users with role-based access control

## Technologies Used

- **Python 3.8+**
- **Flask**: Web framework
- **SQLAlchemy**: ORM for database management
- **MySQL**: Database
- **Bootstrap 5**: Frontend CSS framework
- **Jinja2**: Template engine
- **Flask-Login**: User session management
- **Flask-Bcrypt**: Password hashing

## Prerequisites

- Python 3.8 or higher
- MySQL 5.7 or higher
- pip (Python package installer)

## Installation

### 1. Clone or navigate to the project directory

```bash
cd D:\employee-management-python
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Install required packages

```bash
pip install -r requirements.txt
```

### 5. Create MySQL database

Create a new MySQL database:

```sql
CREATE DATABASE employee_management;
```

### 6. Configure database connection

Edit `app.py` and update the database connection string:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/employee_management'
```

Replace `username` and `password` with your MySQL credentials.

### 7. Initialize the database

Run the application once to create all tables:

```bash
python app.py
```

The database tables will be created automatically on first run.

### 8. Create initial admin user (Optional)

You can create an initial admin user by running a Python script or by registering through the application.

### 9. Run the application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Default Login Credentials

After setting up, you'll need to create your first user. You can either:

1. Use the registration page at `/register`
2. Manually insert a user into the database

## Project Structure

```
employee-management-python/
│
├── app.py                 # Main Flask application
├── models.py              # SQLAlchemy database models
├── requirements.txt       # Python dependencies
├── README.md              # This file
│
├── routes/                # Application routes (blueprints)
│   ├── __init__.py
│   ├── auth.py           # Authentication routes
│   ├── admin.py          # Dashboard routes
│   ├── employee.py       # Employee management
│   ├── department.py     # Department management
│   ├── designation.py    # Designation management
│   ├── attendance.py     # Attendance tracking
│   ├── leave.py          # Leave management
│   ├── payroll.py        # Payroll processing
│   ├── schedule.py       # Schedule management
│   └── user.py           # User management
│
├── templates/             # HTML templates (Jinja2)
│   ├── base.html         # Base template
│   ├── welcome.html      # Welcome page
│   ├── auth/             # Authentication templates
│   └── admin/            # Admin panel templates
│
└── static/                # Static files (CSS, JS, images)
    ├── css/
    ├── js/
    └── uploads/
```

## Features by Role

### Superadmin
- Full system access
- User management
- Role management
- All employee operations
- All department and designation operations
- Attendance management
- Leave management
- Payroll management

### Admin
- Employee management
- Department and designation management
- Attendance tracking
- Leave management
- User management (limited)
- Payroll viewing

### HR Manager
- Employee management
- Department and designation management
- Leave approval/rejection
- Employee profile viewing

### Payroll Manager
- Payroll calculation
- Payroll report generation
- Salary management

### Moderator
- Attendance marking
- Attendance report viewing
- Schedule management

## Usage

1. **Login**: Navigate to `/login` to access the system
2. **Dashboard**: After login, you'll be redirected to a role-specific dashboard
3. **Navigation**: Use the sidebar menu to access different modules
4. **Employee Management**: Add, edit, or remove employees
5. **Attendance**: Mark attendance daily for employees
6. **Leave Requests**: Submit and approve leave requests
7. **Payroll**: Calculate and generate payroll for employees

## API Endpoints

### Authentication
- `GET/POST /login` - User login
- `GET/POST /register` - User registration
- `GET /logout` - User logout

### Employees
- `GET /employee/` - List all employees
- `GET /employee/create` - Show create employee form
- `POST /employee/create` - Create new employee
- `GET /employee/<id>/edit` - Edit employee
- `POST /employee/<id>/delete` - Delete employee

### Departments
- `GET /department/` - List departments
- `GET/POST /department/create` - Create department
- `GET/POST /department/<id>/edit` - Edit department
- `POST /department/<id>/delete` - Delete department

### Attendance
- `GET /attendance/` - View attendance
- `POST /attendance/check` - Mark attendance
- `GET /attendance/report` - Attendance report

### Leave
- `GET /leaves/` - List leave requests
- `GET/POST /leaves/create` - Create leave request
- `GET/POST /leaves/<id>/edit` - Edit leave
- `POST /leaves/<id>/delete` - Delete leave

### Payroll
- `GET /payroll/` - List payrolls
- `GET/POST /payroll/create` - Create payroll
- `POST /payroll/calculate` - Calculate payroll for all
- `GET /payroll/report` - Payroll report

## Database Tables

- `roles` - User roles
- `users` - System users
- `departments` - Organization departments
- `designations` - Job designations
- `schedules` - Work schedules
- `employees` - Employee information
- `attendances` - Attendance records
- `checks` - Check-in/check-out records
- `leaves` - Leave requests
- `salaries` - Employee salary information
- `late_times` - Late arrival records
- `over_times` - Overtime records
- `payrolls` - Payroll records

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open-source and available under the MIT License.

## Support

For support and questions, please create an issue in the repository.

## Acknowledgments

- Original Laravel version by MOHONA678
- Converted to Flask with Python by AI Assistant
- Bootstrap 5 for responsive design
- Flask community for excellent documentation
