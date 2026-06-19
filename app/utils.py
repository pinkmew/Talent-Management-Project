"""
app/utils.py — Reusable decorators for role-based access control.

"""

from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def admin_required(f):
    """Restrict a route to users with the admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # security: Check role after login_required has confirmed authentication.
        if not current_user.is_admin():
            flash('Access denied: this action requires administrator privileges.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function


def manager_required(f):
    """Restrict a route to users with their role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_manager():
            flash('Access denied: this action requires manager or administrator privileges.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function
