
# Quick Setup Guide - Employee Management System (Python Flask)

This guide gives a concise, Windows PowerShell–friendly workflow to get the app running locally and notes for migrations and troubleshooting.

## 🚀 Quick Start (Windows PowerShell)

1. Open PowerShell and go to the project directory:

```powershell
cd D:\employee-management-python
```

2. Create and activate a virtual environment (recommended):

```powershell
python -m venv venv
.\venv\Scripts\activate
```

3. Install Python dependencies:

```powershell
pip install -r requirements.txt
```

4. Create a `.env` file at the project root (used by `python-dotenv`) and set your DB credentials and secret key:

```
SECRET_KEY=change-me
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=employee_management
MYSQL_USER=ems_user
MYSQL_PASSWORD=StrongP@ssw0rd
```

> The app falls back to SQLite if MySQL variables are not present.

5. Initialize the database (two options):

- Option A — use SQL files (direct MySQL client):

```powershell
# load schema and seed (if you prefer explicit SQL loading)
mysql -h 127.0.0.1 -u ems_user -p employee_management < db/mysql/schema.sql
mysql -h 127.0.0.1 -u ems_user -p employee_management < db/mysql/seed.sql
```

- Option B — run the Python initializer (uses SQLAlchemy):

```powershell
python init_db.py
```

6. (Optional but recommended) Use Flask-Migrate for schema migrations:

```powershell
# set the FLASK_APP environment variable for the session
$env:FLASK_APP = 'app.py'
flask db init    # only once when you create migrations folder
flask db migrate -m "Initial schema"
flask db upgrade
```

7. Run the application:

```powershell
python app.py
```

Open http://127.0.0.1:5000 in the browser.

8. Default admin credentials (if seed used):

- Email: `admin@example.com`
- Password: `admin123`

---

## 📁 Project Structure (high-level)

```
employee-management-python/
├── app.py
├── models.py
├── init_db.py
├── requirements.txt
├── README.md
├── SETUP_GUIDE.md
├── routes/
├── templates/
└── static/
```

---

## 🎯 Key features (high level)

- Multi-role authentication (superadmin, admin, hr, payroll manager, moderator)
- Employee CRUD, departments, designations, schedules
- Attendance with check-in/out, monthly reports, auto-generation honoring holidays/weekends/leaves
- Leave management workflow and payroll calculation features

---

## 🔧 Troubleshooting (common issues)

- ModuleNotFoundError: ensure the venv is activated and dependencies installed:

```powershell
.\venv\Scripts\activate
pip install -r requirements.txt
```

- Database connection errors:
  - Confirm MySQL is running
  - Validate credentials in `.env` / `app.py`
  - Confirm the database `employee_management` exists

- Port 5000 in use: run on different port

```powershell
python app.py --port 5001
# or edit the run line in app.py
```

- Missing MySQL driver: install PyMySQL

```powershell
pip install PyMySQL
```

---

## 🔁 Regenerating attendance after data changes

- If you add or edit holidays, or approve leaves outside the UI, regenerate attendance for affected dates. Example (Python REPL):

```python
from database import db
from models import Employee
from datetime import date

employees = Employee.query.filter_by(status='active').all()
for emp in employees:
    emp.generate_attendance(date(2025,11,1), date(2025,11,30))
```

---

## 🧹 Cleaning up accidental commits (venv)

If you accidentally committed `venv/` to git (common), do not push large virtualenv files to the repo. To remove them from the current branch and add `.gitignore`:

```powershell
# add to .gitignore
echo "venv/" >> .gitignore
git rm -r --cached venv
git commit -m "chore: remove venv from repository and add to .gitignore"
git push
```

If you already pushed and want to remove the files from history, use the `git filter-branch` or `git filter-repo` methods (careful — rewriting history).

---

## 🚀 Deployment notes (short)

- Set `DEBUG=False` in production and use environment variables for secrets
- Use a WSGI server (Gunicorn or Waitress on Windows) and a reverse proxy (Nginx)

---

If you'd like, I can also:

- Add a short developer HOWTO with the most common commands
- Provide a small fixture script to create sample employees, schedules, and holidays
- Add unit tests for the attendance generator

Tell me which you'd like next.
