"""
tests/conftest.py — Shared pytest fixtures.

Uses an in-memory SQLite database so tests are fast and isolated —
each test function gets a clean database state.
"""

import pytest
from app import create_app, db as _db
from app.models import User, Employee, Project, Allocation, TalentReview
from datetime import date


@pytest.fixture(scope='session')
def app():
    """Create the Flask application in testing mode."""
    application = create_app('testing')
    return application


@pytest.fixture(scope='function')
def db(app):
    """
    Provide a clean database for each test.
    Creates all tables before the test and drops them after.
    """
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app, db):
    """Test client with a fresh database."""
    return app.test_client()


@pytest.fixture(scope='function')
def seed_users(db, app):
    """
    Create three users (admin, manager, viewer) for access control tests.
    Returns a dict keyed by role.
    """
    with app.app_context():
        admin = User(username='admin', email='admin@test.com', role='admin')
        admin.set_password('Password123!')

        manager = User(username='manager', email='manager@test.com', role='manager')
        manager.set_password('Password123!')

        viewer = User(username='viewer', email='viewer@test.com', role='viewer')
        viewer.set_password('Password123!')

        db.session.add_all([admin, manager, viewer])
        db.session.commit()
        return {'admin': admin, 'manager': manager, 'viewer': viewer}


@pytest.fixture(scope='function')
def seed_employee(db, app):
    """Create a single test employee."""
    with app.app_context():
        emp = Employee(
            employee_number='T001',
            full_name='Test Employee',
            business_area='Test Area',
            current_role='Test Role',
            grade='Analyst',
            talent_segment='Core Performer',
            readiness_level='Ready in 3+ Years',
        )
        db.session.add(emp)
        db.session.commit()
        return emp.id  # Return ID so it can be re-queried in app context


@pytest.fixture(scope='function')
def seed_project(db, app):
    """Create a single test project."""
    with app.app_context():
        proj = Project(
            project_name='Test Project',
            department='Test Dept',
            start_date=date(2024, 1, 1),
            status='Active',
        )
        db.session.add(proj)
        db.session.commit()
        return proj.id


def login(client, email, password):
    """Helper: POST to /login and return the response."""
    return client.post('/login', data={'email': email, 'password': password},
                       follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)
