"""
app/__init__.py — Application factory.

Using the factory pattern (create_app) allows multiple instances to be
created with different configurations — essential for running tests in
isolation without affecting the main application database.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from config import config_map

# ---------------------------------------------------------------------------
# Extension instances — created here, bound to the app inside create_app()
# ---------------------------------------------------------------------------
db = SQLAlchemy()
login_manager = LoginManager()

# SECURITY: Flask-WTF CSRFProtect adds a CSRF token to every form and
# validates it on submission, protecting against Cross-Site Request Forgery
# (OWASP A01: Broken Access Control / A03: Injection via forged requests).
csrf = CSRFProtect()


def create_app(config_name: str = 'default') -> Flask:
    """Create and configure the Flask application."""

    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    # Bind extensions to this app instance
    db.init_app(app)
    csrf.init_app(app)

    # Flask-Login configuration
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'          # Redirect here when login needed
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    # Import models here so SQLAlchemy knows about them before create_all()
    from app import models  # noqa: F401

    # Register blueprints (one per functional area)
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.employees import employees_bp
    from app.routes.projects import projects_bp
    from app.routes.allocations import allocations_bp
    from app.routes.reviews import reviews_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(allocations_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(admin_bp)

    # Inject `now` into every template so the footer year is always current
    from datetime import datetime, timezone

    @app.context_processor
    def inject_now():
        return {'now': datetime.now(timezone.utc)}

    # ------------------------------------------------------------------
    # SECURITY: HTTP Security Headers (OWASP A05 — Security Misconfiguration)
    # These headers are added to every response and tell the browser how
    # to handle content, preventing a range of client-side attacks.
    # ------------------------------------------------------------------
    @app.after_request
    def set_security_headers(response):
        # Prevents the page being embedded in an iframe (clickjacking defence)
        response.headers['X-Frame-Options'] = 'DENY'
        # Stops browsers guessing the content type (MIME-sniffing attack defence)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        # Controls how much referrer info is sent to external sites
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        # Content Security Policy: allow scripts/styles only from self and
        # the CDNs used (Bootstrap, Chart.js, Bootstrap Icons).
        # 'unsafe-inline' for scripts is required for Chart.js inline blocks.
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' cdn.jsdelivr.net 'unsafe-inline'; "
            "style-src 'self' cdn.jsdelivr.net 'unsafe-inline'; "
            "font-src 'self' cdn.jsdelivr.net; "
            "img-src 'self' data:; "
            "connect-src 'self';"
        )
        return response

    # Create all database tables if they do not yet exist
    with app.app_context():
        db.create_all()

    return app
