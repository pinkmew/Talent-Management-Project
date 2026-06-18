"""
app/routes/auth.py — Authentication routes: login, logout, register.

Security notes:
  - Passwords are verified with Werkzeug's check_password_hash — plain text
    is never compared or stored (OWASP A02: Cryptographic Failures).
  - Flask-Login manages the session cookie securely.
  - CSRF token is validated automatically by Flask-WTF on POST.
  - A generic error message is shown on failed login to avoid leaking
    whether an email address is registered (OWASP A07: Auth Failures).
"""

from urllib.parse import urlparse, urljoin

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.models import User, AuditLog
from app.forms import LoginForm, RegisterForm

auth_bp = Blueprint('auth', __name__)


def _is_safe_redirect(target: str) -> bool:
    """
    SECURITY — Open Redirect (OWASP A01):
    Ensure the 'next' redirect target is on the same host.
    An attacker can craft /login?next=http://evil.com — without this
    check the user would be sent to an external site after logging in.
    We only allow relative paths on our own domain.
    """
    ref  = urlparse(request.host_url)
    test = urlparse(urljoin(request.host_url, target))
    return test.scheme in ('http', 'https') and ref.netloc == test.netloc


@auth_bp.route('/')
def index():
    """Root URL — redirect to dashboard if logged in, else to login."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = LoginForm()
    if form.validate_on_submit():
        # SECURITY: Query by email using the ORM — parameterised, no raw SQL.
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()

        # SECURITY: Always check hash — never compare plain text passwords.
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'Welcome back, {user.username}! You are logged in as {user.role}.', 'success')
            # SECURITY: Validate 'next' before redirecting — prevents open redirect.
            next_page = request.args.get('next')
            if not next_page or not _is_safe_redirect(next_page):
                next_page = url_for('dashboard.index')
            return redirect(next_page)
        else:
            # SECURITY: Generic message avoids confirming whether the email exists.
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('auth/login.html', form=form, title='Log In')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """
    Create a new user account.  Restricted to admin users only — this
    prevents self-registration which could be exploited to escalate
    privileges (OWASP A01: Broken Access Control).
    """
    if not current_user.is_admin():
        flash('Access denied: admin only.', 'danger')
        return redirect(url_for('dashboard.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        # Check uniqueness of email and username
        if User.query.filter_by(email=form.email.data.lower()).first():
            flash('That email is already registered.', 'danger')
            return render_template('auth/register.html', form=form, title='Register User')
        if User.query.filter_by(username=form.username.data).first():
            flash('That username is already taken.', 'danger')
            return render_template('auth/register.html', form=form, title='Register User')

        user = User(
            username=form.username.data,
            email=form.email.data.lower().strip(),
            role=form.role.data,
            business_area=form.business_area.data,
        )
        user.set_password(form.password.data)  # Hashes before storing
        db.session.add(user)

        # Audit log entry
        log = AuditLog(
            user_id=current_user.id,
            action_type='CREATE',
            table_changed='users',
            description=f'Admin created user: {user.username} [{user.role}]'
        )
        db.session.add(log)
        db.session.commit()

        flash(f'User "{user.username}" created successfully.', 'success')
        return redirect(url_for('admin.index'))

    return render_template('auth/register.html', form=form, title='Register User')
