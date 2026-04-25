import os
import sys

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from database import db
from models import Document

def migrate():
    with app.app_context():
        # Create documents table
        print("Creating documents table...")
        Document.__table__.create(db.engine, checkfirst=True)
        print("Done.")

if __name__ == '__main__':
    migrate()
