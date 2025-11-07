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
# Employee Management System - Python (Flask)

This repository contains a Flask-based Employee Management System with attendance, leave, payroll, and schedule management.

## Quick overview

- Attendance: check-in/check-out, manual records, monthly reports
- Auto-generation: attendance records can be auto-generated per date (weekends, government/company holidays, approved leaves)
- Holiday management: add/edit/delete holidays which the auto-generator will honor
- Leave management: request/approve leaves which are considered in attendance generation

## Technologies

- Python 3.8+
- Flask, Flask-Login, Flask-Bcrypt
- SQLAlchemy
- Flask-Migrate (optional, recommended)
- Jinja2 + Bootstrap for the UI

## Setup (short)

1. Clone or open the project folder.
2. Create and activate a virtual environment:

```powershell
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Configure the database in `app.py` (MySQL or fallback to SQLite).

5. (Optional) Initialize migrations using Flask-Migrate:

```powershell
# ensure FLASK_APP is set or run via python -m flask
$env:FLASK_APP = 'app.py'
flask db init    # only if migrations folder doesn't already exist
flask db migrate -m "Initial"
flask db upgrade
```

If you don't use Flask-Migrate, running the app once will create tables with SQLAlchemy's `create_all()` behavior (if present). Note: migrations are recommended for production.

6. Run the app:

```powershell
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Key features and how to use them

- Attendance
    - Attendance board: `/attendance/board` — check-in / check-out quickly.
    - Manual add/edit: `/attendance/create` and edit links on index.
    - Monthly report: `/attendance/monthly-report` — choose month, year, and employee.

- Holidays
    - Manage holidays: `/attendance/holidays` — add government/company holidays.
    - When a holiday is added/edited/deleted, the system regenerates attendance records for that date so the status (holiday/weekend/absent/leave) is correct.

- Auto-generate attendance
    - The application auto-generates date-wise attendance for active employees when viewing a date or via the `Employee.generate_attendance(start_date, end_date)` method.
    - Rules applied:
        - If a holiday exists for the date → status = `holiday` (description = holiday name)
        - If weekend (Sat/Sun) → status = `weekend`
        - If approved leave covers the date → status = `leave` (description contains leave type)
        - Otherwise default → status = `absent` until a check-in is recorded

## Database models (high-level)

- `Employee` — employee profile, schedule id, relationships to attendances and leaves
- `Attendance` — date, time_in, time_out, status, description
- `Holiday` — name, date, type (government/company), is_paid
- `Leave` — type, start/end dates, status (pending/approved/rejected)

## Useful routes (summary)

- Auth: `/login`, `/register`, `/logout`
- Employees: `/employee/`, `/employee/create`
- Attendance: `/attendance/`, `/attendance/board`, `/attendance/create`, `/attendance/monthly-report`, `/attendance/holidays`
- Leaves: `/leaves/`, `/leaves/create`

## Notes and troubleshooting

- If you add holidays programmatically, regenerate attendance for affected dates by calling `employee.generate_attendance(date, date)` for each active employee.
- Flask-Migrate is recommended. If you see missing `migrations/env.py` or alembic errors, initialize migrations with `flask db init` (only once) and then `flask db migrate` + `flask db upgrade`.
- If you prefer not to use migrations, ensure SQLAlchemy is configured to create tables on startup (not recommended for production).

## Contribution

Contributions are welcome. Please open an issue or send a pull request with clear details.

## License

MIT

---

If you'd like, I can also:

- Add a short developer HOWTO with common commands
- Add sample data fixtures (employees, schedules, holidays)
- Add unit tests for the attendance generator

Let me know which of the above you'd like next.
- `GET/POST /payroll/create` - Create payroll
