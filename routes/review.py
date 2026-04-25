from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database import db
from models import Employee, PerformanceReview, Notification

bp = Blueprint('review', __name__, url_prefix='/reviews')

@bp.route('/')
@login_required
def index():
    if current_user.role.name not in ['superadmin', 'hr']:
        flash('Access denied. Only HR/Admins can view all reviews.', 'danger')
        return redirect(url_for('auth.login'))
        
    reviews = PerformanceReview.query.order_by(PerformanceReview.created_at.desc()).all()
    employees = Employee.query.filter_by(status='active').all()
    return render_template('admin/review/index.html', reviews=reviews, employees=employees)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if current_user.role.name not in ['superadmin', 'hr']:
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        review_period = request.form.get('review_period')
        rating = int(request.form.get('rating'))
        feedback = request.form.get('feedback')
        goals_achieved = request.form.get('goals_achieved')
        areas_for_improvement = request.form.get('areas_for_improvement')
        status = request.form.get('status', 'published')
        
        employee = Employee.query.get_or_404(employee_id)
        
        review = PerformanceReview(
            employee_id=employee_id,
            reviewer_id=current_user.id,
            review_period=review_period,
            rating=rating,
            feedback=feedback,
            goals_achieved=goals_achieved,
            areas_for_improvement=areas_for_improvement,
            status=status
        )
        db.session.add(review)
        
        if status == 'published':
            # Notify employee
            if employee.email:
                from models import User
                user_account = User.query.filter_by(email=employee.email).first()
                if not user_account and '@' not in employee.email:
                    user_account = User.query.filter_by(email=f"{employee.unique_id}@employee.local").first()
                    
                if user_account:
                    notif = Notification(
                        user_id=user_account.id,
                        message=f"Your performance review for {review_period} has been published.",
                        type='system'
                    )
                    db.session.add(notif)
                    
        db.session.commit()
        flash('Performance Review saved successfully!', 'success')
        return redirect(url_for('review.index'))
        
    employees = Employee.query.filter_by(status='active').all()
    return render_template('admin/review/create.html', employees=employees)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    if current_user.role.name not in ['superadmin', 'hr']:
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
        
    review = PerformanceReview.query.get_or_404(id)
    db.session.delete(review)
    db.session.commit()
    flash('Performance Review deleted successfully!', 'success')
    return redirect(url_for('review.index'))
