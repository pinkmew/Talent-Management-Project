"""
config.py — Application configuration classes.

Loads sensitive values from environment variables so that secrets are
never hard-coded in source code (OWASP A02: Cryptographic Failures /
A05: Security Misconfiguration mitigation).
"""

import os
from dotenv import load_dotenv

# Load .env file if present (local development only)
load_dotenv()


class Config:
    """Base configuration shared by all environments."""

    # SECRET_KEY is used by Flask-WTF for CSRF token signing and by
    # Flask-Login for session cookies.  A missing env var falls back to a
    # development default — production deployments MUST set this.
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-fallback-secret-change-in-prod')

    # SQLAlchemy — defaults to a local SQLite file for development.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'sqlite:///talent_portal.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Suppresses deprecation warning

    # Flask-WTF CSRF protection is enabled globally.
    WTF_CSRF_ENABLED = True


class DevelopmentConfig(Config):
    """Development-specific settings."""
    DEBUG = True


class TestingConfig(Config):
    """Testing-specific settings — uses in-memory SQLite for speed."""
    TESTING = True
    WTF_CSRF_ENABLED = False          # Disable CSRF in tests for simplicity
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret-key'


class ProductionConfig(Config):
    """Production settings — DEBUG must be off."""
    DEBUG = False


# Mapping used by the app factory to select a config by name
config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
