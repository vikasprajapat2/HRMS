#!/usr/bin/env python
"""
change_admin_password.py

Usage:
  - Set the env var NEW_ADMIN_PASSWORD and run: python change_admin_password.py
  - Or run and type a new password at the prompt.

This connects to the configured app (uses app context) and updates (or creates) the user with
email 'admin@example.com'. It hashes the password with Flask-Bcrypt.

Run this on the deployment (one-off job / shell) or locally.
"""
import os
import getpass

from app import app, db, bcrypt
from models import User, Role

EMAIL = os.getenv('ADMIN_EMAIL', 'admin@example.com')
NEW_PW = os.getenv('NEW_ADMIN_PASSWORD')

if not NEW_PW:
    try:
        NEW_PW = getpass.getpass(prompt=f'Enter new password for {EMAIL}: ')
    except Exception:
        # fallback to simple input for non-interactive shells
        NEW_PW = input(f'Enter new password for {EMAIL}: ')

if not NEW_PW:
    print('No password provided; aborting.')
    raise SystemExit(1)

with app.app_context():
    user = User.query.filter_by(email=EMAIL).first()
    if not user:
        print(f'User {EMAIL} not found. Creating new superadmin user.')
        # try to find superadmin role
        role = Role.query.filter_by(name='superadmin').first()
        role_id = role.id if role else None
        user = User(name='Super Admin', email=EMAIL, phone='', role_id=role_id)
        db.session.add(user)

    hashed = bcrypt.generate_password_hash(NEW_PW).decode('utf-8')
    user.password = hashed
    db.session.commit()
    print(f'Success: updated password for {EMAIL}')
