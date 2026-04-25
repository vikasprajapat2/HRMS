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
        is_flexible = request.form.get('is_flexible') == 'on'
        working_hours = request.form.get('working_hours', 8.0, type=float)
        grace_period_minutes = request.form.get('grace_period_minutes', 0, type=int)

        if is_flexible:
            time_in_obj = None
            time_out_obj = None
        else:
            time_in_obj = datetime.strptime(request.form.get('time_in'), '%H:%M').time()
            time_out_obj = datetime.strptime(request.form.get('time_out'), '%H:%M').time()

        schedule = Schedule(
            name=request.form.get('name'),
            time_in=time_in_obj,
            time_out=time_out_obj,
            is_flexible=is_flexible,
            working_hours=working_hours,
            grace_period_minutes=grace_period_minutes
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
        is_flexible = request.form.get('is_flexible') == 'on'
        
        schedule.name = request.form.get('name')
        schedule.is_flexible = is_flexible
        schedule.working_hours = request.form.get('working_hours', 8.0, type=float)
        schedule.grace_period_minutes = request.form.get('grace_period_minutes', 0, type=int)

        if is_flexible:
            schedule.time_in = None
            schedule.time_out = None
        else:
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
