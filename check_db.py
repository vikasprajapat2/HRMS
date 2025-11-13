#!/usr/bin/env python
"""Quick DB connectivity check — run this to verify if deployment can reach the database."""
import os
import pymysql
from urllib.parse import urlparse

# Get DB config from environment
database_url = os.getenv('DATABASE_URL')
if database_url:
    # Parse DATABASE_URL (e.g., mysql+pymysql://user:pass@host:port/db)
    parsed = urlparse(database_url)
    host = parsed.hostname or 'localhost'
    user = parsed.username or 'root'
    password = parsed.password or ''
    port = parsed.port or 3306
    db = parsed.path.lstrip('/') if parsed.path else 'hrms_db'
else:
    # Fall back to individual env vars
    host = os.getenv('MYSQL_HOST', 'localhost')
    user = os.getenv('MYSQL_USER', 'root')
    password = os.getenv('MYSQL_PASSWORD', '1234')
    port = int(os.getenv('MYSQL_PORT', 3306))
    db = os.getenv('MYSQL_DATABASE', 'hrms_db')

print(f"Checking DB connection...")
print(f"Host: {host}")
print(f"Port: {port}")
print(f"User: {user}")
print(f"Database: {db}")
print()

try:
    conn = pymysql.connect(
        host=host,
        user=user,
        password=password,
        port=port,
        database=db,
        connect_timeout=5,
    )
    print("✓ SUCCESS: Connected to database!")
    
    # Try a simple query
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM user")
        count = cur.fetchone()[0]
        print(f"✓ Query OK: Found {count} users in database")
    
    conn.close()
except pymysql.Error as e:
    print(f"✗ FAILED: {e}")
    print()
    print("Common causes:")
    print("  1. HOST/PORT unreachable (firewall, wrong DNS, localhost on Render)")
    print("  2. USER/PASSWORD incorrect")
    print("  3. DATABASE doesn't exist")
    print("  4. MySQL server is down")
except Exception as e:
    print(f"✗ ERROR: {e}")
