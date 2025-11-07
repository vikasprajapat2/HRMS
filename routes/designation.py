from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from database import db
from models import Designation

bp = Blueprint('designation', __name__, url_prefix='/designation')

@bp.route('/')
@login_required
def index():
    designations = Designation.query.all()
    return render_template('admin/designation/index.html', designations=designations)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        designation = Designation(
            name=request.form.get('name'),
            description=request.form.get('description')
        )
        db.session.add(designation)
        db.session.commit()
        flash('Designation created successfully!', 'success')
        return redirect(url_for('designation.index'))
    return render_template('admin/designation/create.html')

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    designation = Designation.query.get_or_404(id)
    if request.method == 'POST':
        designation.name = request.form.get('name')
        designation.description = request.form.get('description')
        db.session.commit()
        flash('Designation updated successfully!', 'success')
        return redirect(url_for('designation.index'))
    return render_template('admin/designation/edit.html', designation=designation)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    designation = Designation.query.get_or_404(id)
    db.session.delete(designation)
    db.session.commit()
    flash('Designation deleted successfully!', 'success')
    return redirect(url_for('designation.index'))
