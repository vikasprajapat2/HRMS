from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from database import db
from models import Leave, Employee
from datetime import datetime, date

bp = Blueprint('leave', __name__, url_prefix='/leaves')

@bp.route('/')
@login_required
def index():
    status_filter = request.args.get('status', 'all')
    employee_id = request.args.get('employee_id')
    
    query = Leave.query
    
    if status_filter != 'all':
        query = query.filter(Leave.status == status_filter)
    if employee_id:
        query = query.filter(Leave.employee_id == employee_id)
    
    leaves = query.order_by(Leave.start_date.desc()).all()
    employees = Employee.query.order_by(Employee.firstname).all()
    
    return render_template('admin/leave/index.html', 
                         leaves=leaves, 
                         employees=employees, 
                         current_status=status_filter,
                         selected_employee=employee_id)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
        
        if start_date > end_date:
            flash('Start date cannot be after end date', 'error')
            employees = Employee.query.order_by(Employee.firstname).all()
            return render_template('admin/leave/create.html', employees=employees)
        
        # Check for overlapping leaves
        existing_leave = Leave.query.filter(
            Leave.employee_id == employee_id,
            Leave.status != 'rejected',
            Leave.start_date <= end_date,
            Leave.end_date >= start_date
        ).first()
        
        if existing_leave:
            flash('Employee already has an approved/pending leave in this date range', 'error')
            employees = Employee.query.order_by(Employee.firstname).all()
            return render_template('admin/leave/create.html', employees=employees)
        
        leave = Leave(
            employee_id=employee_id,
            leave_type=request.form.get('leave_type'),
            start_date=start_date,
            end_date=end_date,
            reason=request.form.get('reason'),
            status='pending'
        )
        db.session.add(leave)
        db.session.commit()
        flash('Leave request submitted successfully!', 'success')
        return redirect(url_for('leave.index'))
    
    employees = Employee.query.order_by(Employee.firstname).all()
    return render_template('admin/leave/create.html', employees=employees)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    leave = Leave.query.get_or_404(id)
    
    # Don't allow editing of processed leaves
    if leave.status in ['approved', 'rejected']:
        flash('Cannot edit processed leave requests', 'error')
        return redirect(url_for('leave.index'))
    
    if request.method == 'POST':
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
        
        if start_date > end_date:
            flash('Start date cannot be after end date', 'error')
            employees = Employee.query.order_by(Employee.firstname).all()
            return render_template('admin/leave/edit.html', leave=leave, employees=employees)
        
        # Check for overlapping leaves (excluding this leave)
        existing_leave = Leave.query.filter(
            Leave.employee_id == leave.employee_id,
            Leave.id != leave.id,
            Leave.status != 'rejected',
            Leave.start_date <= end_date,
            Leave.end_date >= start_date
        ).first()
        
        if existing_leave:
            flash('Employee already has an approved/pending leave in this date range', 'error')
            employees = Employee.query.order_by(Employee.firstname).all()
            return render_template('admin/leave/edit.html', leave=leave, employees=employees)
        
        leave.leave_type = request.form.get('leave_type')
        leave.start_date = start_date
        leave.end_date = end_date
        leave.reason = request.form.get('reason')
        
        db.session.commit()
        flash('Leave updated successfully!', 'success')
        return redirect(url_for('leave.index'))
    
    employees = Employee.query.order_by(Employee.firstname).all()
    return render_template('admin/leave/edit.html', leave=leave, employees=employees)

@bp.route('/<int:id>/process', methods=['POST'])
@login_required
def process_leave(id):
    leave = Leave.query.get_or_404(id)
    action = request.form.get('action')
    
    if action not in ['approve', 'reject']:
        return jsonify({'error': 'Invalid action'}), 400
    
    if leave.status != 'pending':
        return jsonify({'error': 'Can only process pending leaves'}), 400
    
    leave.status = 'approved' if action == 'approve' else 'rejected'
    leave.processed_by = current_user.id
    leave.processed_at = datetime.now()
    
    db.session.commit()
    flash(f'Leave {leave.status}', 'success')
    return redirect(url_for('leave.index'))

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    leave = Leave.query.get_or_404(id)
    
    # Don't allow deleting processed leaves
    if leave.status in ['approved', 'rejected']:
        flash('Cannot delete processed leave requests', 'error')
        return redirect(url_for('leave.index'))
    
    db.session.delete(leave)
    db.session.commit()
    flash('Leave deleted successfully!', 'success')
    return redirect(url_for('leave.index'))

@bp.route('/report')
@login_required
def report():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    status = request.args.get('status', 'all')
    employee_id = request.args.get('employee_id')
    
    query = Leave.query
    
    if start_date and end_date:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        query = query.filter(Leave.start_date >= start, Leave.end_date <= end)
    
    if status != 'all':
        query = query.filter(Leave.status == status)
    
    if employee_id:
        query = query.filter(Leave.employee_id == employee_id)
    
    leaves = query.order_by(Leave.start_date.desc()).all()
    employees = Employee.query.order_by(Employee.firstname).all()
    
    return render_template('admin/leave/report.html',
                         leaves=leaves,
                         employees=employees,
                         selected_status=status,
                         selected_employee=employee_id,
                         start_date=start_date,
                         end_date=end_date)
