# **DEPLOYMENT GUIDE - FIX THE WHITE PAGE ISSUE**

## Problem
After login, the dashboard shows a **white/blank page** instead of the dashboard content.

**Root Cause:** The deployed instance cannot connect to the MySQL database because `DATABASE_URL` environment variable is not set. Without it, the app falls back to `localhost` which doesn't exist on Render/Railway.

---

## Solution: Set DATABASE_URL Environment Variable

### Step 1: Get Your Database Connection String

You need your MySQL database connection details. Depending on where your DB is hosted:

**Option A: If using a managed DB (Render MySQL, Railway MySQL, AWS RDS, etc.)**
- Find the connection URL in your database provider's dashboard
- It should look like: `mysql+pymysql://user:password@host:port/database`

**Option B: If you have a local MySQL that you want to use (NOT recommended for production)**
- Connection string: `mysql+pymysql://root:1234@your-public-ip:3306/hrms_db`

### Step 2: Add DATABASE_URL to Your Render/Railway Service

#### For **Render**:
1. Go to your service dashboard
2. Click **"Environment"** (left sidebar)
3. Click **"Add Environment Variable"**
4. Key: `DATABASE_URL`
5. Value: `mysql+pymysql://user:password@host:port/database`
6. Click Save
7. Your service will auto-restart with the new variable

#### For **Railway**:
1. Go to your service dashboard
2. Click the **"Variables"** tab
3. Add new variable:
   - Key: `DATABASE_URL`
   - Value: `mysql+pymysql://user:password@host:port/database`
4. Click Deploy

---

## Step 3: Initialize Database (One-Time)

After setting `DATABASE_URL`, you need to initialize the database tables.

### Option A: Use Render/Railway One-Off Job

**Render:**
```bash
python init_db.py
```
(Run from the one-off job UI in Render dashboard)

**Railway:**
```bash
python init_db.py
```
(Run from the Railway CLI or shell)

### Option B: Use the Diagnostic Script

```bash
python check_db.py
```
This will:
1. Test if the DB is reachable
2. Show any connection errors
3. Tell you if tables exist

---

## Step 4: Test Login

1. Go to your deployed URL
2. Login with:
   - Email: `admin@example.com`
   - Password: `1234`
3. You should now see the **dashboard with metrics** (not a blank page)

---

## Troubleshooting

If you still see a blank page after init:

1. **Run the diagnostics:**
   ```bash
   python check_db.py
   ```
   Paste the output in the issue.

2. **Check the logs:**
   - Render: Service → Logs tab
   - Railway: Logs tab
   - Look for any ERROR or Traceback lines around the time you logged in

3. **Common errors:**
   - `Connection refused`: Host/port is wrong or DB is down
   - `Access denied`: Username or password is wrong
   - `Unknown database 'hrms_db'`: Run `init_db.py` to create tables

---

## DATABASE_URL Format Reference

### MySQL (Standard)
```
mysql+pymysql://user:password@host:port/database
```

### Examples:
- Local: `mysql+pymysql://root:1234@localhost:3306/hrms_db`
- Remote: `mysql+pymysql://admin:mypassword@db.example.com:3306/hrms_db`
- With special chars in password: `mysql+pymysql://admin:p%40ssw0rd@host:3306/hrms_db` (URL-encoded)

---

## Questions?

Paste the output of `python check_db.py` and your server logs if you're still stuck.
