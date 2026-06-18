"""
app/routes/dashboard.py — Dashboard with summary cards and Chart.js data.

All data is fetched via SQLAlchemy ORM — no raw SQL (OWASP A03 mitigation).
Login is required for every route in this blueprint.
"""

from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from sqlalchemy import func

from app import db
from app.models import Employee, Project, Allocation, TalentReview

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def index():
    """Main dashboard with KPI cards including overallocation alert."""

    total_employees = Employee.query.count()
    active_projects = Project.query.filter_by(status='Active').count()
    open_actions    = TalentReview.query.filter(
        TalentReview.status.in_(['Open', 'In Progress'])
    ).count()

    avg_alloc_result = db.session.query(
        func.avg(Allocation.allocation_percentage)
    ).scalar()
    avg_alloc = avg_alloc_result or 0

    # Overallocation: employees whose total allocation across all projects > 100%
    overallocated = (
        db.session.query(Employee.full_name, func.sum(Allocation.allocation_percentage).label('total'))
        .join(Allocation, Allocation.employee_id == Employee.id)
        .group_by(Employee.id)
        .having(func.sum(Allocation.allocation_percentage) > 100)
        .all()
    )

    # High flight-risk count for the KPI card
    high_flight_risk = Employee.query.filter_by(flight_risk='High').count()

    return render_template(
        'dashboard/index.html',
        title='Dashboard',
        total_employees=total_employees,
        active_projects=active_projects,
        open_actions=open_actions,
        avg_allocation=round(avg_alloc, 1),
        overallocated=overallocated,
        high_flight_risk=high_flight_risk,
    )


# ---------------------------------------------------------------------------
# Chart data API endpoints — JSON consumed by Chart.js in the browser.
# ---------------------------------------------------------------------------

@dashboard_bp.route('/dashboard/chart/business-area')
@login_required
def chart_business_area():
    rows = (
        db.session.query(Employee.business_area, func.count(Employee.id))
        .group_by(Employee.business_area).all()
    )
    return jsonify({'labels': [r[0] for r in rows], 'values': [r[1] for r in rows]})


@dashboard_bp.route('/dashboard/chart/talent-segment')
@login_required
def chart_talent_segment():
    rows = (
        db.session.query(Employee.talent_segment, func.count(Employee.id))
        .group_by(Employee.talent_segment).all()
    )
    return jsonify({'labels': [r[0] for r in rows], 'values': [r[1] for r in rows]})


@dashboard_bp.route('/dashboard/chart/allocation-by-project')
@login_required
def chart_allocation_by_project():
    rows = (
        db.session.query(Project.project_name, func.sum(Allocation.allocation_percentage))
        .join(Allocation, Allocation.project_id == Project.id)
        .group_by(Project.project_name).all()
    )
    return jsonify({'labels': [r[0] for r in rows], 'values': [r[1] for r in rows]})


@dashboard_bp.route('/dashboard/chart/review-status')
@login_required
def chart_review_status():
    rows = (
        db.session.query(TalentReview.status, func.count(TalentReview.id))
        .group_by(TalentReview.status).all()
    )
    return jsonify({'labels': [r[0] for r in rows], 'values': [r[1] for r in rows]})


@dashboard_bp.route('/dashboard/chart/flight-risk')
@login_required
def chart_flight_risk():
    """Employee count grouped by flight risk level."""
    rows = (
        db.session.query(Employee.flight_risk, func.count(Employee.id))
        .group_by(Employee.flight_risk).all()
    )
    return jsonify({'labels': [r[0] for r in rows], 'values': [r[1] for r in rows]})


@dashboard_bp.route('/dashboard/chart/overallocation')
@login_required
def chart_overallocation():
    """Total allocation % per employee — highlights anyone over 100%."""
    rows = (
        db.session.query(Employee.full_name, func.sum(Allocation.allocation_percentage).label('total'))
        .join(Allocation, Allocation.employee_id == Employee.id)
        .group_by(Employee.id)
        .order_by(func.sum(Allocation.allocation_percentage).desc())
        .all()
    )
    return jsonify({'labels': [r[0] for r in rows], 'values': [r[1] for r in rows]})
