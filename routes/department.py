from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from database import db
from models import Department

bp = Blueprint('department', __name__, url_prefix='/department')

@bp.route('/')
@login_required
def index():
    departments = Department.query.all()
    return render_template('admin/department/index.html', departments=departments)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        department = Department(
            name=request.form.get('name'),
            description=request.form.get('description')
        )
        db.session.add(department)
        db.session.commit()
        flash('Department created successfully!', 'success')
        return redirect(url_for('department.index'))
    return render_template('admin/department/create.html')

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    department = Department.query.get_or_404(id)
    if request.method == 'POST':
        department.name = request.form.get('name')
        department.description = request.form.get('description')
        db.session.commit()
        flash('Department updated successfully!', 'success')
        return redirect(url_for('department.index'))
    return render_template('admin/department/edit.html', department=department)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    department = Department.query.get_or_404(id)
    db.session.delete(department)
    db.session.commit()
    flash('Department deleted successfully!', 'success')
    return redirect(url_for('department.index'))
