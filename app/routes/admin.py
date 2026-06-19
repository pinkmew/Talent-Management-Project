"""
app/routes/admin.py — Admin panel and audit log.
"""

from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user

from app.models import AuditLog, User, Employee, Project, TalentReview
from app.utils import admin_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin')
@login_required
@admin_required
def index():
    """Admin overview page with system stats."""
    stats = {
        'total_users':     User.query.count(),
        'total_employees': Employee.query.count(),
        'total_projects':  Project.query.count(),
        'open_reviews':    TalentReview.query.filter(
            TalentReview.status.in_(['Open', 'In Progress'])
        ).count(),
    }
    recent_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()
    return render_template('admin/index.html', stats=stats,
                           recent_logs=recent_logs, title='Admin Panel')


@admin_bp.route('/admin/audit-log')
@login_required
@admin_required
def audit_log():
    """Full audit log — paginated, newest first."""
    page = 1
    per_page = 50
    logs = (
        AuditLog.query
        .order_by(AuditLog.timestamp.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    return render_template('admin/audit_log.html', logs=logs, title='Audit Log')


@admin_bp.route('/admin/users')
@login_required
@admin_required
def users():
    """List all registered users."""
    all_users = User.query.order_by(User.username).all()
    return render_template('admin/users.html', users=all_users, title='Manage Users')
