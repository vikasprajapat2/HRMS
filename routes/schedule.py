from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from database import db
from models import Schedule
from datetime import datetime

bp = Blueprint('schedule', __name__, url_prefix='/schedule')

@bp.route('/')
@login_required
def index():
    schedules = Schedule.query.all()
    return render_template('admin/schedule/index.html', schedules=schedules)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        schedule = Schedule(
            name=request.form.get('name'),
            time_in=datetime.strptime(request.form.get('time_in'), '%H:%M').time(),
            time_out=datetime.strptime(request.form.get('time_out'), '%H:%M').time()
        )
        db.session.add(schedule)
        db.session.commit()
        flash('Schedule created successfully!', 'success')
        return redirect(url_for('schedule.index'))
    return render_template('admin/schedule/create.html')

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    schedule = Schedule.query.get_or_404(id)
    if request.method == 'POST':
        schedule.name = request.form.get('name')
        schedule.time_in = datetime.strptime(request.form.get('time_in'), '%H:%M').time()
        schedule.time_out = datetime.strptime(request.form.get('time_out'), '%H:%M').time()
        db.session.commit()
        flash('Schedule updated successfully!', 'success')
        return redirect(url_for('schedule.index'))
    return render_template('admin/schedule/edit.html', schedule=schedule)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    schedule = Schedule.query.get_or_404(id)
    db.session.delete(schedule)
    db.session.commit()
    flash('Schedule deleted successfully!', 'success')
    return redirect(url_for('schedule.index'))
