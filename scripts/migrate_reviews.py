import os
import sys

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from database import db
from models import PerformanceReview

def migrate():
    with app.app_context():
        # Create performance_reviews table
        print("Creating performance_reviews table...")
        PerformanceReview.__table__.create(db.engine, checkfirst=True)
        print("Done.")

if __name__ == '__main__':
    migrate()
