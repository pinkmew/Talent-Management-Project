"""
app/routes/reviews.py — Talent Review CRUD routes.

"""

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timezone

from app import db
from app.models import TalentReview, Employee, AuditLog
from app.forms import TalentReviewForm
from app.utils import manager_required, admin_required

reviews_bp = Blueprint('reviews', __name__)


@reviews_bp.route('/reviews')
@login_required
def index():
    reviews = (
        TalentReview.query
        .join(Employee)
        .order_by(TalentReview.review_date.desc())
        .all()
    )
    status_counts = {
        'Open':        TalentReview.query.filter_by(status='Open').count(),
        'In Progress': TalentReview.query.filter_by(status='In Progress').count(),
        'Complete':    TalentReview.query.filter_by(status='Complete').count(),
    }
    return render_template('reviews/index.html', reviews=reviews,
                           status_counts=status_counts, title='Talent Reviews')


@reviews_bp.route('/reviews/add/<int:employee_id>', methods=['GET', 'POST'])
@login_required
@manager_required
def add(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    form = TalentReviewForm()

    if form.validate_on_submit():
        review = TalentReview(
            employee_id=employee.id,
            reviewed_by=current_user.id,
            review_date=form.review_date.data,
            performance_rating=form.performance_rating.data,
            potential_rating=form.potential_rating.data,
            development_action=form.development_action.data,
            status=form.status.data,
        )
        db.session.add(review)
        db.session.flush()

        log = AuditLog(
            user_id=current_user.id,
            action_type='CREATE',
            table_changed='talent_reviews',
            record_id=review.id,
            description=f'Created review for {employee.full_name} — status: {review.status}'
        )
        db.session.add(log)
        db.session.commit()

        flash(f'Review created for {employee.full_name}.', 'success')
        return redirect(url_for('employees.detail', employee_id=employee.id))

    return render_template('reviews/add.html', form=form, employee=employee, title='Add Review')


@reviews_bp.route('/reviews/<int:review_id>/edit', methods=['GET', 'POST'])
@login_required
@manager_required
def edit(review_id):
    review   = TalentReview.query.get_or_404(review_id)
    employee = review.employee
    form     = TalentReviewForm(obj=review)

    if form.validate_on_submit():
        review.review_date        = form.review_date.data
        review.performance_rating = form.performance_rating.data
        review.potential_rating   = form.potential_rating.data
        review.development_action = form.development_action.data
        review.status             = form.status.data
        review.updated_at         = datetime.now(timezone.utc)

        log = AuditLog(
            user_id=current_user.id,
            action_type='UPDATE',
            table_changed='talent_reviews',
            record_id=review.id,
            description=f'Updated review ID {review.id} for {employee.full_name}'
        )
        db.session.add(log)
        db.session.commit()

        flash('Review updated successfully.', 'success')
        return redirect(url_for('employees.detail', employee_id=employee.id))

    return render_template('reviews/edit.html', form=form, review=review,
                           employee=employee, title='Edit Review')


@reviews_bp.route('/reviews/<int:review_id>/close', methods=['POST'])
@login_required
@manager_required
def close(review_id):
    """Mark a review as Complete."""
    review = TalentReview.query.get_or_404(review_id)
    review.status     = 'Complete'
    review.updated_at = datetime.now(timezone.utc)

    log = AuditLog(
        user_id=current_user.id,
        action_type='UPDATE',
        table_changed='talent_reviews',
        record_id=review.id,
        description=f'Closed review ID {review.id} for employee ID {review.employee_id}'
    )
    db.session.add(log)
    db.session.commit()

    flash('Review marked as Complete.', 'success')
    return redirect(url_for('reviews.index'))
