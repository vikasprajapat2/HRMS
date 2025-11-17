import sys, os, traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app
from database import db
from models import User
from flask_login import login_user

email = 'vikas@gmail.com'

with app.app_context():
    user = User.query.filter_by(email=email).first()
    if not user:
        print('User not found')
    else:
        try:
            # create a request context for dashboard
            with app.test_request_context('/user/dashboard'):
                login_user(user)
                # import the dashboard view
                from routes.user import dashboard as dashboard_view
                result = dashboard_view()
                # If result is a template render, it will be a string
                print('Dashboard view returned successfully. Type:', type(result))
                # print a short preview
                if isinstance(result, str):
                    print(result[:500])
        except Exception as e:
            print('Exception while rendering dashboard:')
            traceback.print_exc()
