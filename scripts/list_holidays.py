"""Script to list holidays from the app database.

This script ensures the project root is on sys.path so imports like `from app import app`
work when the script is executed from the `scripts/` folder.
"""
import os
import sys

# Ensure project root (parent of this scripts folder) is on sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import app
from models import Holiday

with app.app_context():
    holidays = Holiday.query.order_by(Holiday.date).all()
    if not holidays:
        print('No holidays found in the database.')
    else:
        print(f"Found {len(holidays)} holiday(s):")
        for h in holidays:
            date_str = h.date.isoformat() if getattr(h, 'date', None) else 'N/A'
            print(f"- {date_str} | {h.name} | type={getattr(h, 'type', '')} | paid={'Yes' if getattr(h, 'is_paid', False) else 'No'} | {h.description or ''}")
