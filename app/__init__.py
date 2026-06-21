"""
app/__init__.py — Application factory.

"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from config import config_map

# Extension instances 
db = SQLAlchemy()
login_manager = LoginManager()

csrf = CSRFProtect()


def create_app(config_name: str = 'default') -> Flask:
    """Create and configure the Flask application."""

    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    # Bind extensions to this app instance
    db.init_app(app)
    csrf.init_app(app)

    # Flask Login configuration
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'          # Redirect here when login needed
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    # Import models here so SQLAlchemy knows about them before create_all()
    from app import models  # noqa: F401

    # Register blueprints
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

    # Inject into every template so the footer year is current
    from datetime import datetime, timezone

    @app.context_processor
    def inject_now():
        return {'now': datetime.now(timezone.utc)}

    
    @app.after_request
    def set_security_headers(response):
        # Prevents the page being embedded in an ifram
        response.headers['X-Frame-Options'] = 'DENY'
        # Stops browsers guessing the content type
        response.headers['X-Content-Type-Options'] = 'nosniff'
        # Controls how much referrer info is sent to external sites
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' cdn.jsdelivr.net 'unsafe-inline'; "
            "style-src 'self' cdn.jsdelivr.net 'unsafe-inline'; "
            "font-src 'self' cdn.jsdelivr.net; "
            "img-src 'self' data:; "
            "connect-src 'self';"
        )
        return response

    from flask import render_template as rt

    @app.errorhandler(404)
    def not_found(e):
        return rt('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return rt('errors/403.html'), 403

    with app.app_context():
        db.create_all()
        if not app.config.get('TESTING'):
            _auto_seed_if_empty()

    return app


def _auto_seed_if_empty():
    from sqlalchemy.exc import IntegrityError
    from app.models import User
    if User.query.count() == 0:
        try:
            from app.seed_data import seed_demo_data
            seed_demo_data(db)
        except IntegrityError:
            db.session.rollback()
