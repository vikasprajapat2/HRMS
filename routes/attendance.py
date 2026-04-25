from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database import db
from models import Attendance, Employee, Check, Holiday, Leave, WorkingDayConfig
from datetime import datetime, time, timedelta
from calendar import monthrange
from collections import defaultdict

bp = Blueprint('attendance', __name__, url_prefix='/attendance')


@bp.route('/')
@login_required
def index():
    # Accept an optional ISO date string via query param, otherwise use today
    date_arg = request.args.get('date')
    if date_arg:
        try:
            date_obj = datetime.fromisoformat(date_arg).date()
        except Exception:
            date_obj = datetime.now().date()
    else:
        date_obj = datetime.now().date()

    # Auto-generate attendance records for all active employees if they don't exist
    employees = Employee.query.filter_by(status='active').all()
    for employee in employees:
        employee.generate_attendance(date_obj, date_obj)

    # 1. Chart Data (Current month till last day)
    year = date_obj.year
    month = date_obj.month
    _, last_day = monthrange(year, month)
    
    chart_labels = []
    chart_on_time = []
    chart_late = []
    
    start_date = datetime(year, month, 1).date()
    end_date = datetime(year, month, last_day).date()
    month_attendances = Attendance.query.filter(Attendance.date.between(start_date, end_date)).all()
    
    day_stats = defaultdict(lambda: {'on_time': 0, 'late': 0})
    for att in month_attendances:
        if att.status == 'present' and att.time_in and att.employee.schedule:
            schedule = att.employee.schedule
            if schedule.is_flexible:
                # Flexible shifts aren't late based on check-in time
                day_stats[att.date.day]['on_time'] += 1
            else:
                allowed_time = (datetime.combine(att.date, schedule.time_in) + timedelta(minutes=schedule.grace_period_minutes)).time()
                if att.time_in > allowed_time:
                    day_stats[att.date.day]['late'] += 1
                else:
                    day_stats[att.date.day]['on_time'] += 1

    for d in range(1, last_day + 1):
        curr = datetime(year, month, d).date()
        day_str = f"{d}-{curr.strftime('%a')}"
        chart_labels.append(day_str)
        chart_on_time.append(day_stats[d]['on_time'])
        chart_late.append(day_stats[d]['late'])

    # 2. Daily stats (for `date_obj`) grouped by Department
    from models import Department
    departments = Department.query.all()
    dept_stats = []
    
    todays_attendances = Attendance.query.filter_by(date=date_obj).all()
    emp_login_lists = {'logged_in': [], 'on_time': [], 'late': []}
    
    for dept in departments:
        dept_info = {
            'name': dept.name,
            'total': len(dept.employees),
            'on_time': 0,
            'late': 0,
            'leave': 0
        }
        dept_stats.append(dept_info)
        
    dept_map = {d['name']: d for d in dept_stats}
    
    for att in todays_attendances:
        emp = att.employee
        dept_name = emp.department.name if emp.department else None
        
        att_status_detail = "Absent"
        if att.status == 'leave':
            if dept_name in dept_map: dept_map[dept_name]['leave'] += 1
        elif att.status == 'present':
            is_late = False
            if att.time_in and emp.schedule:
                if emp.schedule.is_flexible:
                    is_late = False
                else:
                    allowed_time = (datetime.combine(att.date, emp.schedule.time_in) + timedelta(minutes=emp.schedule.grace_period_minutes)).time()
                    if att.time_in > allowed_time:
                        is_late = True
                
            if is_late:
                if dept_name in dept_map: dept_map[dept_name]['late'] += 1
                att_status_detail = "Late"
            else:
                if dept_name in dept_map: dept_map[dept_name]['on_time'] += 1
                att_status_detail = "On-time"

            emp_data = {
                'id': emp.id,
                'name': f"{emp.firstname} {emp.lastname}",
                'designation': emp.designation.name if emp.designation else "Regular",
                'image': emp.image,
                'initials': f"{emp.firstname[0]}{emp.lastname[0]}" if emp.firstname and emp.lastname else "E",
                'status': att_status_detail,
                'time_in': att.time_in.strftime('%I:%M %p') if att.time_in else "-",
                'time_out': att.time_out.strftime('%I:%M %p') if att.time_out else "-"
            }
            emp_login_lists['logged_in'].append(emp_data)
            if is_late:
                emp_login_lists['late'].append(emp_data)
            else:
                emp_login_lists['on_time'].append(emp_data)

    # 3. Backlog calculation 
    backlog_list = []
    for att in todays_attendances:
        if att.status in ['absent', 'leave'] and len(backlog_list) < 4:
            emp = att.employee
            backlog_list.append({
                'name': f"{emp.firstname} {emp.lastname}",
                'designation': emp.designation.name if emp.designation else "Regular",
                'image': emp.image,
                'initials': f"{emp.firstname[0]}{emp.lastname[0]}" if emp.firstname and emp.lastname else "E",
                'no_days': 1,
                'pending_hrs': '8h 0m'
            })

    return render_template(
        'admin/attendance/index.html', 
        date=date_obj,
        chart_labels=chart_labels,
        chart_on_time=chart_on_time,
        chart_late=chart_late,
        dept_stats=dept_stats,
        emp_lists=emp_login_lists,
        backlog_list=backlog_list,
        month_name=date_obj.strftime('%b'),
        year_name=date_obj.year
    )


@bp.route('/board')
@login_required
def board():
    """Attendance board for today: shows all employees and their attendance records for today.

    Only users in roles `superadmin`, `admin`, `moderator`, or `hr` may access the board.
    Actions (check-in / check-out) post to the existing `/attendance/check` endpoint.
    """
    # restrict access to managers and HR
    if not current_user.is_authenticated or current_user.role.name not in ['superadmin', 'hr']:
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))
    current_date = datetime.now().date()
    employees = Employee.query.order_by(Employee.firstname).all()
    attendances = Attendance.query.filter_by(date=current_date).all()
    # Map employee_id -> attendance for quick lookup in template
    attendance_map = {a.employee_id: a for a in attendances}
    return render_template('admin/attendance/board.html', employees=employees, attendance_map=attendance_map, date=current_date)


@bp.route('/check', methods=['POST'])
@login_required
def check():
    employee_id = request.form.get('employee_id')
    action = request.form.get('action')  # 'in' or 'out'
    
    time_str = request.form.get('time')
    if time_str:
        from datetime import datetime as _dt
        current_time = _dt.strptime(time_str, '%H:%M').time()
    else:
        current_time = datetime.now().time()
        
    current_date = datetime.now().date()
    
    # Only allow privileged roles to mark attendance
    if not current_user.is_authenticated or current_user.role.name not in ['superadmin', 'hr']:
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))

    attendance = Attendance.query.filter_by(employee_id=employee_id, date=current_date).first()
    
    if action == 'in':
        if not attendance:
            attendance = Attendance(
                employee_id=employee_id,
                date=current_date,
                time_in=current_time,
                status='present'
            )
            db.session.add(attendance)
        else:
            attendance.time_in = current_time
    elif action == 'out':
        if attendance:
            attendance.time_out = current_time
        else:
            flash('No check-in record found!', 'warning')
            return redirect(url_for('attendance.board'))
    
    db.session.commit()
    flash(f'Check {action} recorded successfully!', 'success')
    return redirect(url_for('attendance.board'))


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a manual attendance record.

    Only `superadmin`, `admin`, `moderator`, and `hr` may create manual records.
    """
    if not current_user.is_authenticated or current_user.role.name not in ['superadmin', 'hr']:
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        date_str = request.form.get('date')
        time_in_str = request.form.get('time_in')
        time_out_str = request.form.get('time_out')
        status = request.form.get('status') or 'present'

        try:
            date_obj = datetime.fromisoformat(date_str).date()
        except Exception:
            date_obj = datetime.now().date()

        time_in_obj = None
        time_out_obj = None
        from datetime import datetime as _dt
        try:
            if time_in_str:
                time_in_obj = _dt.strptime(time_in_str, '%H:%M').time()
            if time_out_str:
                time_out_obj = _dt.strptime(time_out_str, '%H:%M').time()
        except Exception:
            pass

        attendance = Attendance(employee_id=employee_id, date=date_obj, time_in=time_in_obj, time_out=time_out_obj, status=status)
        db.session.add(attendance)
        db.session.commit()
        flash('Attendance record created.', 'success')
        return redirect(url_for('attendance.index', date=date_obj.isoformat()))

    employees = Employee.query.order_by(Employee.firstname).all()
    default_date = datetime.now().date().isoformat()
    return render_template('admin/attendance/create.html', employees=employees, default_date=default_date)


@bp.route('/edit/<int:attendance_id>', methods=['GET', 'POST'])
@login_required
def edit(attendance_id):
    # Only privileged roles can edit attendance
    if not current_user.is_authenticated or current_user.role.name not in ['superadmin', 'hr']:
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))

    attendance = Attendance.query.get_or_404(attendance_id)
    if request.method == 'POST':
        date_str = request.form.get('date')
        time_in_str = request.form.get('time_in')
        time_out_str = request.form.get('time_out')
        status = request.form.get('status')

        try:
            attendance.date = datetime.fromisoformat(date_str).date()
        except Exception:
            pass

        from datetime import datetime as _dt
        try:
            attendance.time_in = _dt.strptime(time_in_str, '%H:%M').time() if time_in_str else None
        except Exception:
            attendance.time_in = None
        try:
            attendance.time_out = _dt.strptime(time_out_str, '%H:%M').time() if time_out_str else None
        except Exception:
            attendance.time_out = None

        attendance.status = status or attendance.status
        db.session.commit()
        flash('Attendance updated.', 'success')
        return redirect(url_for('attendance.index', date=attendance.date.isoformat()))

    employees = Employee.query.order_by(Employee.firstname).all()
    default_date = attendance.date.isoformat() if attendance and attendance.date else datetime.now().date().isoformat()
    return render_template('admin/attendance/create.html', attendance=attendance, employees=employees, default_date=default_date)


@bp.route('/delete/<int:attendance_id>', methods=['POST'])
@login_required
def delete(attendance_id):
    # Only privileged roles can delete attendance
    if not current_user.is_authenticated or current_user.role.name not in ['superadmin', 'hr']:
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))

    attendance = Attendance.query.get_or_404(attendance_id)
    date = attendance.date
    db.session.delete(attendance)
    db.session.commit()
    flash('Attendance deleted.', 'success')
    return redirect(url_for('attendance.index', date=date.isoformat()))


@bp.route('/monthly-report')
@login_required
def monthly_report():
    """Generate monthly attendance report with statistics."""
    # Only privileged roles can view reports
    if not current_user.is_authenticated or current_user.role.name not in ['superadmin', 'hr']:
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))

    # Get month and year from query params, default to current month
    year = int(request.args.get('year', datetime.now().year))
    month = int(request.args.get('month', datetime.now().month))
    employee_id = request.args.get('employee_id')
    
    # Calculate start and end dates for the month
    _, last_day = monthrange(year, month)
    start_date = datetime(year, month, 1).date()
    end_date = datetime(year, month, last_day).date()
    
    # Base query
    query = Attendance.query.filter(Attendance.date.between(start_date, end_date))
    if employee_id:
        query = query.filter(Attendance.employee_id == employee_id)
    
    # Get all employees for filter dropdown
    employees = Employee.query.order_by(Employee.firstname).all()
    
    # Fetch attendance records
    attendances = query.order_by(Attendance.employee_id, Attendance.date).all()
    
    # Calculate statistics per employee
    stats = defaultdict(lambda: {
        'present': 0,
        'absent': 0,
        'late': 0,
        'early_out': 0,
        'working_hours': timedelta(),
        'attendance_percentage': 0
    })
    
    for attendance in attendances:
        emp_stats = stats[attendance.employee_id]
        
        if attendance.status == 'present':
            emp_stats['present'] += 1
            
            # Calculate working hours if both in/out times exist
            if attendance.time_in and attendance.time_out:
                time_in = datetime.combine(attendance.date, attendance.time_in)
                time_out = datetime.combine(attendance.date, attendance.time_out)
                working_hours = time_out - time_in
                emp_stats['working_hours'] += working_hours
                
                # Check if employee's schedule exists and compare
                if attendance.employee.schedule:
                    schedule = attendance.employee.schedule
                    if schedule.is_flexible:
                        # For flexible shifts, check if they met working hours instead of late time
                        if working_hours.total_seconds() / 3600 < float(schedule.working_hours):
                            emp_stats['early_out'] += 1 # Technically under-hours
                    else:
                        allowed_time = (datetime.combine(attendance.date, schedule.time_in) + timedelta(minutes=schedule.grace_period_minutes)).time()
                        if attendance.time_in > allowed_time:
                            emp_stats['late'] += 1
                        if attendance.time_out < datetime.combine(attendance.date, schedule.time_out).time():
                            emp_stats['early_out'] += 1
        else:
            emp_stats['absent'] += 1
        
        # Calculate attendance percentage
        total_days = emp_stats['present'] + emp_stats['absent']
        if total_days > 0:
            emp_stats['attendance_percentage'] = (emp_stats['present'] / total_days) * 100
            
    import calendar
    cal_grid = calendar.monthcalendar(year, month)
    
    # Map attendances by employee and date day to easily render in calendar
    att_by_emp_day = defaultdict(dict)
    for att in attendances:
        att_by_emp_day[att.employee_id][att.date.day] = att
    
    return render_template('admin/attendance/monthly_report.html',
                         attendances=attendances,
                         att_by_emp_day=att_by_emp_day,
                         cal_grid=cal_grid,
                         employees=employees,
                         stats=stats,
                         year=year,
                         month=month,
                         selected_employee=employee_id,
                         month_name=datetime(year, month, 1).strftime('%B'),
                         datetime=datetime)

@bp.route('/report')
@login_required
def report():
    # Only privileged roles can view general reports
    if not current_user.is_authenticated or current_user.role.name not in ['superadmin', 'hr']:
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Attendance.query
    if start_date and end_date:
        query = query.filter(Attendance.date.between(start_date, end_date))
    
    attendances = query.all()
    return render_template('admin/attendance/report.html', attendances=attendances)

@bp.route('/holidays')
@login_required
def holidays():
    # Only allow superadmin, admin or hr to view/manage holidays
    if not current_user.is_authenticated or current_user.role.name not in ['superadmin', 'hr']:
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))

    holidays = Holiday.query.order_by(Holiday.date).all()
    return render_template('admin/attendance/holidays.html', holidays=holidays)

@bp.route('/holidays/create', methods=['GET', 'POST'])
@login_required
def create_holiday():
    # Only superadmin, admin or hr can create holidays
    if not current_user.is_authenticated or current_user.role.name not in ['superadmin', 'hr']:
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        name = request.form.get('name')
        date_str = request.form.get('date')
        description = request.form.get('description')
        holiday_type = request.form.get('type')
        is_paid = request.form.get('is_paid', 'true') == 'true'

        try:
            date_obj = datetime.fromisoformat(date_str).date()
        except Exception:
            flash('Invalid date format', 'error')
            return redirect(url_for('attendance.holidays'))

        holiday = Holiday(
            name=name,
            date=date_obj,
            description=description,
            type=holiday_type,
            is_paid=is_paid
        )
        db.session.add(holiday)
        db.session.commit()

        # Regenerate attendance records for this date
        employees = Employee.query.filter_by(status='active').all()
        for employee in employees:
            employee.generate_attendance(date_obj, date_obj)

        flash('Holiday added successfully', 'success')
        return redirect(url_for('attendance.holidays'))

    return render_template('admin/attendance/holiday_form.html')

@bp.route('/holidays/<int:holiday_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_holiday(holiday_id):
    # Only superadmin, admin or hr can edit holidays
    if not current_user.is_authenticated or current_user.role.name not in ['superadmin', 'hr']:
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))

    holiday = Holiday.query.get_or_404(holiday_id)
    
    if request.method == 'POST':
        holiday.name = request.form.get('name')
        holiday.description = request.form.get('description')
        holiday.type = request.form.get('type')
        holiday.is_paid = request.form.get('is_paid', 'true') == 'true'
        
        date_str = request.form.get('date')
        try:
            holiday.date = datetime.fromisoformat(date_str).date()
        except Exception:
            flash('Invalid date format', 'error')
            return redirect(url_for('attendance.holidays'))

        db.session.commit()

        # Regenerate attendance records for this date
        employees = Employee.query.filter_by(status='active').all()
        for employee in employees:
            employee.generate_attendance(holiday.date, holiday.date)

        flash('Holiday updated successfully', 'success')
        return redirect(url_for('attendance.holidays'))

    return render_template('admin/attendance/holiday_form.html', holiday=holiday)

@bp.route('/holidays/<int:holiday_id>/delete', methods=['POST'])
@login_required
def delete_holiday(holiday_id):
    # Only superadmin, admin or hr can delete holidays
    if not current_user.is_authenticated or current_user.role.name not in ['superadmin', 'hr']:
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))

    holiday = Holiday.query.get_or_404(holiday_id)
    date = holiday.date
    
    db.session.delete(holiday)
    db.session.commit()

    # Regenerate attendance records for this date
    employees = Employee.query.filter_by(status='active').all()
    for employee in employees:
        employee.generate_attendance(date, date)

    flash('Holiday deleted successfully', 'success')
    return redirect(url_for('attendance.holidays'))


@bp.route('/working-days')
@login_required
def manage_working_days():
    """View and manage working days configuration (which days are working vs. non-working).
    
    Only superadmin, admin, and hr can access.
    """
    if not current_user.is_authenticated or current_user.role.name not in ['superadmin', 'hr']:
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))
    
    # Get or create working day configs for all 7 days
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    configs = []
    for i in range(7):
        config = WorkingDayConfig.query.filter_by(weekday=i).first()
        if not config:
            # Create default: Mon-Fri (0-4) working, Sat-Sun (5-6) non-working
            config = WorkingDayConfig(
                weekday=i,
                day_name=day_names[i],
                is_working_day=i < 5
            )
            db.session.add(config)
        configs.append(config)
    db.session.commit()
    
    return render_template('admin/attendance/working_days.html', configs=configs)


@bp.route('/working-days/<int:weekday>/toggle', methods=['POST'])
@login_required
def toggle_working_day(weekday):
    """Toggle a specific weekday between working/non-working.
    
    Only superadmin, admin, and hr can toggle.
    """
    if not current_user.is_authenticated or current_user.role.name not in ['superadmin', 'hr']:
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))
    
    if weekday < 0 or weekday > 6:
        flash('Invalid weekday', 'danger')
        return redirect(url_for('attendance.manage_working_days'))
    
    config = WorkingDayConfig.query.filter_by(weekday=weekday).first()
    if not config:
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        config = WorkingDayConfig(
            weekday=weekday,
            day_name=day_names[weekday],
            is_working_day=weekday < 5
        )
        db.session.add(config)
    
    # Toggle the status
    config.is_working_day = not config.is_working_day
    db.session.commit()
    
    status = 'working day' if config.is_working_day else 'non-working day (weekend)'
    flash(f'{config.day_name} is now marked as {status}', 'success')
    
    return redirect(url_for('attendance.manage_working_days'))

