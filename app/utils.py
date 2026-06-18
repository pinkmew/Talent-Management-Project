"""
app/utils.py — Reusable decorators for role-based access control.

OWASP A01: Broken Access Control mitigation.

These decorators are applied to route functions.  When a user with
insufficient privileges reaches a protected endpoint they receive:
  - HTTP 403 (via flash + redirect rather than abort, to keep the
    Bootstrap layout consistent)

Usage:
    @login_required          # Flask-Login: must be logged in
    @admin_required          # Must have role == 'admin'
    @manager_required        # Must have role in ('admin', 'manager')
"""

from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def admin_required(f):
    """Restrict a route to users with the 'admin' role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # SECURITY: Check role AFTER login_required has confirmed authentication.
        if not current_user.is_admin():
            flash('Access denied: this action requires administrator privileges.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function


def manager_required(f):
    """Restrict a route to users with the 'admin' or 'manager' role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_manager():
            flash('Access denied: this action requires manager or administrator privileges.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function
