import sqlite3
from datetime import date

db_path = 'instance/employee_management.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 2026 Indian Holidays (Common ones)
holidays = [
    ('New Year\'s Day', '2026-01-01', 'New Year celebration', 'government', 1),
    ('Republic Day', '2026-01-26', 'National holiday', 'government', 1),
    ('Holi', '2026-03-04', 'Festival of colors', 'religious', 1),
    ('Good Friday', '2026-04-03', 'Religious holiday', 'religious', 1),
    ('Eid-ul-Fitr', '2026-03-20', 'Religious holiday', 'religious', 1),
    ('Labor Day', '2026-05-01', 'International Workers\' Day', 'government', 1),
    ('Independence Day', '2026-08-15', 'National holiday', 'government', 1),
    ('Gandhi Jayanti', '2026-10-02', 'National holiday', 'government', 1),
    ('Diwali', '2026-11-08', 'Festival of lights', 'religious', 1),
    ('Christmas', '2026-12-25', 'Religious holiday', 'religious', 1),
]

for name, dt, desc, h_type, is_paid in holidays:
    cursor.execute('''
        INSERT OR IGNORE INTO holidays (name, date, description, type, is_paid)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, dt, desc, h_type, is_paid))

conn.commit()
print(f"Seeded {len(holidays)} holidays for 2026.")
conn.close()
