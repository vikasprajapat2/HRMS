from flask import Blueprint, jsonify, request
from database import db
from models import Employee, Department, Designation
from functools import wraps
import os

bp = Blueprint('api', __name__, url_prefix='/api')

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Allow testing without API key if not set in environment
        # In a real production app, you would ALWAYS enforce this
        expected_api_key = os.getenv('API_KEY', 'default-dev-api-key')
        
        api_key = request.headers.get('X-API-Key')
        if api_key and api_key == expected_api_key:
            return f(*args, **kwargs)
        else:
            return jsonify({"error": "Unauthorized. Invalid or missing X-API-Key header."}), 401
    return decorated_function


@bp.route('/employees', methods=['GET'])
@require_api_key
def get_employees():
    """Get a list of all active employees."""
    employees = Employee.query.filter_by(status='active').all()
    
    results = []
    for emp in employees:
        results.append({
            'id': emp.id,
            'unique_id': emp.unique_id,
            'firstname': emp.firstname,
            'lastname': emp.lastname,
            'email': emp.email,
            'phone': emp.phone,
            'department': emp.department.name if emp.department else None,
            'designation': emp.designation.name if emp.designation else None,
            'status': emp.status
        })
        
    return jsonify({
        'status': 'success',
        'count': len(results),
        'data': results
    })


@bp.route('/employees/<int:id>', methods=['GET'])
@require_api_key
def get_employee(id):
    """Get details for a specific employee."""
    emp = Employee.query.get(id)
    
    if not emp:
        return jsonify({"error": "Employee not found"}), 404
        
    data = {
        'id': emp.id,
        'unique_id': emp.unique_id,
        'firstname': emp.firstname,
        'lastname': emp.lastname,
        'email': emp.email,
        'phone': emp.phone,
        'address': emp.address,
        'dob': emp.dob.strftime('%Y-%m-%d') if emp.dob else None,
        'gender': emp.gender,
        'religion': emp.religion,
        'marital': emp.marital,
        'department': emp.department.name if emp.department else None,
        'designation': emp.designation.name if emp.designation else None,
        'status': emp.status,
        'joined_at': emp.created_at.strftime('%Y-%m-%d %H:%M:%S') if emp.created_at else None
    }
    
    return jsonify({
        'status': 'success',
        'data': data
    })
