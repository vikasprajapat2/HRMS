from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from database import db
from models import LeaveType

bp = Blueprint('leave_type', __name__, url_prefix='/leave-types')

@bp.route('/')
@login_required
def index():
    leave_types = LeaveType.query.all()
    return render_template('admin/leave_type/index.html', leave_types=leave_types)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        
        if LeaveType.query.filter_by(name=name.lower()).first():
            flash('Leave type already exists!', 'error')
            return redirect(url_for('leave_type.create'))
            
        leave_type = LeaveType(
            name=name.lower(),
            description=request.form.get('description'),
            days_allowed=int(request.form.get('days_allowed') or 0)
        )
        db.session.add(leave_type)
        db.session.commit()
        flash('Leave type created successfully!', 'success')
        return redirect(url_for('leave_type.index'))
        
    return render_template('admin/leave_type/create.html')

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    leave_type = LeaveType.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        
        existing = LeaveType.query.filter(LeaveType.name == name.lower(), LeaveType.id != id).first()
        if existing:
            flash('Leave type name already exists!', 'error')
            return redirect(url_for('leave_type.edit', id=id))
            
        leave_type.name = name.lower()
        leave_type.description = request.form.get('description')
        leave_type.days_allowed = int(request.form.get('days_allowed') or 0)
        
        db.session.commit()
        flash('Leave type updated successfully!', 'success')
        return redirect(url_for('leave_type.index'))
        
    return render_template('admin/leave_type/edit.html', leave_type=leave_type)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    leave_type = LeaveType.query.get_or_404(id)
    db.session.delete(leave_type)
    db.session.commit()
    flash('Leave type deleted successfully!', 'success')
    return redirect(url_for('leave_type.index'))
