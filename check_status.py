#!/usr/bin/env python
"""Quick DB diagnostics"""
import os
from app import app, db
from models import User, Role

with app.app_context():
    print('=== DATABASE CONNECTION INFO ===')
    print(f'Database URL: {app.config.get("SQLALCHEMY_DATABASE_URI", "Not set")}')
    print(f'Using SQLite Fallback: {app.config.get("USE_DB_FALLBACK", False)}')
    print()
    
    print('=== USERS ===')
    users = User.query.all()
    print(f'Total users: {len(users)}')
    for u in users:
        print(f'  - ID: {u.id}, Email: {u.email}, Name: {u.name}, Role ID: {u.role_id}')
    
    print()
    print('=== ROLES ===')
    roles = Role.query.all()
    print(f'Total roles: {len(roles)}')
    for r in roles:
        print(f'  - ID: {r.id}, Name: {r.name}')
