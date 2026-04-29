import sqlite3
import os

db_path = 'instance/employee_management.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("--- Table: holidays ---")
try:
    cursor.execute("PRAGMA table_info(holidays)")
    cols = cursor.fetchall()
    if cols:
        for col in cols:
            print(col)
    else:
        print("Table 'holidays' does not exist or has no columns.")
except Exception as e:
    print(f"Error checking holidays: {e}")

print("\n--- Table: attendances ---")
try:
    cursor.execute("PRAGMA table_info(attendances)")
    cols = cursor.fetchall()
    for col in cols:
        print(col)
except Exception as e:
    print(f"Error checking attendances: {e}")

conn.close()
