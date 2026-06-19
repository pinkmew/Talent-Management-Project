"""
config.py — Application configuration classes.

"""

import os
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()


class Config:
    """Base configuration shared by all environments."""

    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-fallback-secret-change-in-prod')

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
    """Production settings"""
    DEBUG = False


# Mapping used by the app factory.
config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
