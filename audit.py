import json
from datetime import datetime, date, time
from decimal import Decimal
from flask import request, has_request_context
from flask_login import current_user
from sqlalchemy import event, inspect
from database import db
from models import AuditLog

class AuditJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date, time)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)

def row_to_dict(obj, mask_password=True):
    """Convert an SQLAlchemy object to dict, masking sensitive fields."""
    result = {}
    try:
        for c in obj.__table__.columns:
            val = getattr(obj, c.name)
            if mask_password and c.name == 'password':
                result[c.name] = '***' if val else None
            else:
                result[c.name] = val
    except Exception:
        pass
    return result

def get_actor_and_ip():
    """Safely fetch the current actor_id and ip from Flask context"""
    actor_id = None
    ip_address = None
    if has_request_context():
        if current_user and current_user.is_authenticated:
            actor_id = current_user.id
        ip_address = request.remote_addr
    return actor_id, ip_address

def after_insert_listener(mapper, connection, target):
    # Prevent infinite recursion when AuditLog itself is inserted
    if isinstance(target, AuditLog):
        return

    actor_id, ip_address = get_actor_and_ip()
    new_data = row_to_dict(target)
    
    # We use connection.execute directly to avoid infinite SQLAlchemy session loops
    table = AuditLog.__table__
    connection.execute(
        table.insert().values(
            actor_id=actor_id,
            action='CREATE',
            model=target.__class__.__name__,
            record_id=getattr(target, 'id', None),
            old_data=None,
            new_data=json.dumps(new_data, cls=AuditJSONEncoder),
            ip_address=ip_address,
            created_at=datetime.utcnow()
        )
    )

def after_update_listener(mapper, connection, target):
    if isinstance(target, AuditLog):
        return

    actor_id, ip_address = get_actor_and_ip()
    
    # Using inspect to check which columns actually changed
    state = inspect(target)
    
    old_data = {}
    new_data = {}
    changed = False
    
    for attr in state.attrs:
        hist = attr.history
        if hist.has_changes():
            changed = True
            
            # Mask passwords if they were changed
            if attr.key == 'password':
                old_data[attr.key] = '***'
                new_data[attr.key] = '***'
            else:
                old_data[attr.key] = hist.deleted[0] if hist.deleted else None
                new_data[attr.key] = hist.added[0] if hist.added else None
    
    # Only insert if there are actual diffs
    if changed:
        table = AuditLog.__table__
        connection.execute(
            table.insert().values(
                actor_id=actor_id,
                action='UPDATE',
                model=target.__class__.__name__,
                record_id=getattr(target, 'id', None),
                old_data=json.dumps(old_data, cls=AuditJSONEncoder),
                new_data=json.dumps(new_data, cls=AuditJSONEncoder),
                ip_address=ip_address,
                created_at=datetime.utcnow()
            )
        )

def after_delete_listener(mapper, connection, target):
    if isinstance(target, AuditLog):
        return

    actor_id, ip_address = get_actor_and_ip()
    old_data = row_to_dict(target)
    
    table = AuditLog.__table__
    connection.execute(
        table.insert().values(
            actor_id=actor_id,
            action='DELETE',
            model=target.__class__.__name__,
            record_id=getattr(target, 'id', None),
            old_data=json.dumps(old_data, cls=AuditJSONEncoder),
            new_data=None,
            ip_address=ip_address,
            created_at=datetime.utcnow()
        )
    )

def register_audit_listeners():
    """Register hooks globally for all SQLAlchemy models"""
    event.listen(db.Model, 'after_insert', after_insert_listener, propagate=True)
    event.listen(db.Model, 'after_update', after_update_listener, propagate=True)
    event.listen(db.Model, 'after_delete', after_delete_listener, propagate=True)
