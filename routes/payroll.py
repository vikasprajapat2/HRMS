from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from database import db
from models import Payroll, Employee, Salary
from datetime import datetime
from decimal import Decimal

bp = Blueprint('payroll', __name__, url_prefix='/payroll')

@bp.route('/')
@login_required
def index():
    payrolls = Payroll.query.all()
    return render_template('admin/payroll/index.html', payrolls=payrolls)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        month = request.form.get('month')
        year = int(request.form.get('year'))
        
        employee = Employee.query.get(employee_id)
        if not employee or not employee.salary:
            flash('Employee salary not configured!', 'warning')
            return redirect(url_for('payroll.create'))
        
        basic_salary = employee.salary.basic_salary
        allowances = Decimal(request.form.get('allowances', 0))
        overtime_amount = Decimal(request.form.get('overtime_amount', 0))
        deductions = Decimal(request.form.get('deductions', 0))
        net_salary = basic_salary + allowances + overtime_amount - deductions
        
        payroll = Payroll(
            employee_id=employee_id,
            month=month,
            year=year,
            basic_salary=basic_salary,
            allowances=allowances,
            overtime_amount=overtime_amount,
            deductions=deductions,
            net_salary=net_salary,
            status='pending'
        )
        
        db.session.add(payroll)
        db.session.commit()
        flash('Payroll created successfully!', 'success')
        return redirect(url_for('payroll.index'))
    
    employees = Employee.query.all()
    return render_template('admin/payroll/create.html', employees=employees)

@bp.route('/report')
@login_required
def report():
    month = request.args.get('month')
    year = request.args.get('year')
    
    query = Payroll.query
    if month and year:
        query = query.filter_by(month=month, year=int(year))
    
    payrolls = query.all()
    return render_template('admin/payroll/report.html', payrolls=payrolls)

@bp.route('/calculate', methods=['POST'])
@login_required
def calculate():
    # Calculate payroll for all employees for a given month
    month = request.form.get('month')
    year = int(request.form.get('year'))
    
    employees = Employee.query.filter_by(status='active').all()
    
    for employee in employees:
        if not employee.salary:
            continue
        
        # Check if payroll already exists
        existing = Payroll.query.filter_by(
            employee_id=employee.id,
            month=month,
            year=year
        ).first()
        
        if existing:
            continue
        
        basic_salary = employee.salary.basic_salary
        net_salary = basic_salary
        
        payroll = Payroll(
            employee_id=employee.id,
            month=month,
            year=year,
            basic_salary=basic_salary,
            net_salary=net_salary
        )
        db.session.add(payroll)
    
    db.session.commit()
    flash('Payroll calculated for all employees!', 'success')
    return redirect(url_for('payroll.index'))
