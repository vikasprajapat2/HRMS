import sys, os, traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app
from models import User
from flask_login import login_user

email = 'vikas@gmail.com'

with app.app_context():
    user = User.query.filter_by(email=email).first()
    if not user:
        print('User not found')
    else:
        try:
            with app.test_request_context('/user/attendance'):
                from routes.user import attendance_list, leaves_list, payrolls_list
                from flask_login import login_user
                login_user(user)
                print('Rendering attendance...')
                print(type(attendance_list()))
                print('Rendering leaves...')
                print(type(leaves_list()))
                print('Rendering payrolls...')
                print(type(payrolls_list()))
        except Exception:
            traceback.print_exc()
