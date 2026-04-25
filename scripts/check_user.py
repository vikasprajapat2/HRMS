import sys, os
# ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import app
from database import db
from models import User
from flask_bcrypt import Bcrypt

import argparse

parser = argparse.ArgumentParser(description="Check user credentials")
parser.add_argument("--email", default=os.environ.get("CHECK_EMAIL", "admin@example.com"), help="User email to check")
parser.add_argument("--password", default=os.environ.get("CHECK_PASSWORD", "admin123"), help="User password to check")
args, _ = parser.parse_known_args()

email = args.email
password = args.password

with app.app_context():
    user = User.query.filter_by(email=email).first()
    if not user:
        print(f'User with email {email} not found')
    else:
        print('User found:')
        print(f'  id: {user.id}')
        print(f'  name: {getattr(user, "name", None)}')
        print(f'  email: {user.email}')
        print(f'  role: {user.role.name if user.role else None}')
        print(f'  status: {user.status}')
        print(f'  password_hash: {user.password[:20]}...')
        bcrypt = Bcrypt(app)
        try:
            matches = bcrypt.check_password_hash(user.password, password)
        except Exception as e:
            matches = f'Error checking password: {e}'
        print(f'  password_matches("{password}"): {matches}')
