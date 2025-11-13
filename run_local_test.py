from app import app
from database import db
from models import User, Role

with app.app_context():
    user = User.query.filter_by(email='admin@example.com').first()
    print('Admin user exists:', bool(user))
    if user:
        print('id:', user.id, 'email:', user.email, 'role_id:', user.role_id)
        try:
            role = user.role
            print('role object:', role)
            print('role name:', role.name if role else None)
        except Exception as e:
            print('Error accessing user.role:', e)

# Use test client to simulate login
with app.test_client() as c:
    r = c.get('/login')
    print('\nGET /login', r.status_code)
    r = c.post('/login', data={'email':'admin@example.com','password':'1234'}, follow_redirects=True)
    print('POST /login status', r.status_code)
    text = r.get_data(as_text=True)
    print('Response length:', len(text))
    print('\nResponse snippet:')
    print(text[:2000])
