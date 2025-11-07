# Quick Setup Guide - Employee Management System (Python Flask)

## 🚀 Quick Start

### Step 1: Install Python Dependencies

Open PowerShell in the project directory and run:

```powershell
cd D:\employee-management-python

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Setup MySQL Database

1. Open MySQL and create a new database:

```sql
CREATE DATABASE employee_management;
```

2. Configure environment variables in a `.env` file at the project root:

```
SECRET_KEY=change-me
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=employee_management
MYSQL_USER=ems_user
MYSQL_PASSWORD=StrongP@ssw0rd
```

The app will automatically use MySQL if these variables are present; otherwise it falls back to SQLite.

### Step 3: Initialize Database (two options)

```powershell
python init_db.py
```

Option A) Use the provided SQL schema and seed (MySQL client):

```
mysql -h 127.0.0.1 -u ems_user -p employee_management < db/mysql/schema.sql
mysql -h 127.0.0.1 -u ems_user -p employee_management < db/mysql/seed.sql
```

Option B) Use the Python initializer (creates tables and seeds via SQLAlchemy):

```
python init_db.py
```

This will create all tables and insert sample data including:
- Default roles (superadmin, admin, hr, payroll, moderator)
- Default superadmin user
- Sample departments and designations
- Sample work schedules

### Step 4: Run the Application

```powershell
python app.py
```

The application will be available at: **http://localhost:5000**

### Step 5: Login

Use these default credentials:
- **Email**: admin@example.com
- **Password**: admin123

---

## 📁 Project Structure

```
employee-management-python/
│
├── app.py                      # Main Flask application
├── models.py                   # Database models (SQLAlchemy)
├── init_db.py                  # Database initialization script
├── requirements.txt            # Python dependencies
├── README.md                   # Comprehensive documentation
├── SETUP_GUIDE.md             # This file
│
├── routes/                     # Application routes (Blueprints)
│   ├── __init__.py
│   ├── auth.py                # Authentication (login, logout, register)
│   ├── admin.py               # Dashboard routes
│   ├── employee.py            # Employee CRUD operations
│   ├── department.py          # Department management
│   ├── designation.py         # Designation management
│   ├── attendance.py          # Attendance tracking
│   ├── leave.py               # Leave management
│   ├── payroll.py             # Payroll processing
│   ├── schedule.py            # Work schedule management
│   └── user.py                # User management
│
├── templates/                  # HTML templates (Jinja2)
│   ├── base.html              # Base layout with sidebar
│   ├── welcome.html           # Landing page
│   ├── auth/                  # Authentication pages
│   │   ├── login.html
│   │   ├── register.html
│   │   └── forgot-password.html
│   └── admin/                 # Admin panel pages
│       └── dashboard.html
│
└── static/                     # Static files
    ├── css/
    │   └── style.css          # Custom CSS
    ├── js/
    └── uploads/               # User uploads
```

---

## 🎯 Key Features

### ✅ Implemented Features

1. **Multi-Role Authentication System**
   - Superadmin, Admin, HR, Payroll Manager, Moderator
   - Role-based access control
   - Secure password hashing with Bcrypt

2. **Employee Management**
   - Create, Read, Update, Delete employees
   - Employee profiles with personal details
   - Department and designation assignment
   - Work schedule assignment

3. **Department & Designation Management**
   - Organize employees by departments
   - Define job designations
   - Full CRUD operations

4. **Attendance System**
   - Daily attendance tracking
   - Check-in/Check-out functionality
   - Attendance reports
   - Date-based filtering

5. **Leave Management**
   - Leave request submission
   - Leave approval/rejection
   - Leave types and status tracking

6. **Payroll System**
   - Monthly payroll calculation
   - Salary components (basic, allowances, deductions)
   - Overtime calculation
   - Payroll reports

7. **Schedule Management**
   - Define work shifts
   - Time-in and time-out schedules
   - Assign schedules to employees

8. **User Management**
   - Create and manage system users
   - Assign roles to users
   - User status management

9. **Modern UI with Bootstrap 5**
   - Responsive design
   - Clean and intuitive interface
   - Gradient cards and modern styling
   - Font Awesome icons

---

## 🔧 Troubleshooting

### Issue: ModuleNotFoundError

**Solution**: Make sure you've activated the virtual environment and installed all dependencies:
```powershell
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: Database Connection Error

**Solution**: 
1. Make sure MySQL is running
2. Verify database credentials in `app.py`
3. Ensure the database `employee_management` exists

### Issue: Port 5000 Already in Use

**Solution**: Change the port in `app.py` (last line):
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Issue: No module named 'MySQLdb'

**Solution**: Install PyMySQL which is a pure Python MySQL driver:
```powershell
pip install PyMySQL
```

---

## 🎨 Customization

### Change Database

Edit `app.py` line 11 to use a different database:

**SQLite:**
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employee_management.db'
```

**PostgreSQL:**
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/employee_management'
```

### Change Secret Key

Edit `app.py` line 10 for production:
```python
app.config['SECRET_KEY'] = 'your-unique-secret-key-here'
```

### Modify Branding

- Update `templates/base.html` line 25 to change the application name
- Modify `static/css/style.css` to customize colors and styles

---

## 📊 Database Schema

### Main Tables

- **roles**: User roles and permissions
- **users**: System users with authentication
- **departments**: Organization departments
- **designations**: Job titles and positions
- **schedules**: Work shifts and timings
- **employees**: Employee personal information
- **attendances**: Daily attendance records
- **leaves**: Leave requests and approvals
- **salaries**: Employee salary information
- **payrolls**: Monthly payroll records
- **late_times**: Late arrival tracking
- **over_times**: Overtime hours tracking
- **checks**: Check-in/check-out records

---

## 🔐 Security Considerations

1. **Change default credentials** immediately after first login
2. **Use strong secret key** in production
3. **Enable HTTPS** for production deployment
4. **Set DEBUG=False** in production
5. **Implement rate limiting** for login attempts
6. **Regular database backups**
7. **Update dependencies** regularly

---

## 🚀 Deployment

### For Production Deployment:

1. Set debug mode to False in `app.py`:
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

2. Use a production WSGI server like Gunicorn:
```powershell
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

3. Set up a reverse proxy with Nginx or Apache

4. Use environment variables for sensitive data

---

## 📝 Next Steps

1. ✅ Basic setup complete
2. ⬜ Add employee list and detail pages
3. ⬜ Complete attendance marking interface
4. ⬜ Add payroll calculation reports
5. ⬜ Implement email notifications
6. ⬜ Add export functionality (PDF, Excel)
7. ⬜ Implement search and filtering
8. ⬜ Add data visualization dashboards

---

## 📞 Support

For issues or questions:
1. Check the README.md file
2. Review the code comments
3. Refer to Flask documentation: https://flask.palletsprojects.com/

---

## 🙏 Acknowledgments

- Original Laravel version: [MOHONA678/employee-management-system](https://github.com/MOHONA678/employee-management-system)
- Converted to Flask with Python, HTML, CSS, and Bootstrap 5
- Bootstrap 5 for responsive UI
- Font Awesome for icons
- Flask community for excellent documentation

---

**Enjoy your Employee Management System! 🎉**
