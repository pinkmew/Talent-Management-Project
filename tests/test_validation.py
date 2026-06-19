"""
tests/test_validation.py — Input validation and security tests.

"""

from tests.conftest import login
from app.models import Allocation


class TestAllocationValidation:

    def test_allocation_above_100_rejected(self, client, seed_users,
                                           seed_employee, seed_project, app):
        """
        An allocation_percentage over 100 must be rejected by the server-side
        """
        login(client, 'admin@test.com', 'Password123!')
        resp = client.post('/allocations/add', data={
            'employee_id': seed_employee,
            'project_id': seed_project,
            'assigned_role': 'Developer',
            'allocation_percentage': 150,  # Invalid value
            'start_date': '2024-01-01',
            'end_date': '',
        }, follow_redirects=True)
        # Server returns the form page with an error.
        assert resp.status_code == 200
        # Confirm no allocation was created in the database
        with app.app_context():
            alloc = Allocation.query.filter_by(
                employee_id=seed_employee, project_id=seed_project
            ).first()
            assert alloc is None

    def test_allocation_negative_rejected(self, client, seed_users,
                                          seed_employee, seed_project, app):
        """Negative allocation percentage is also rejected."""
        login(client, 'admin@test.com', 'Password123!')
        client.post('/allocations/add', data={
            'employee_id': seed_employee,
            'project_id': seed_project,
            'assigned_role': 'Developer',
            'allocation_percentage': -10,
            'start_date': '2024-01-01',
            'end_date': '',
        }, follow_redirects=True)
        with app.app_context():
            assert Allocation.query.count() == 0

    def test_valid_allocation_boundary_100(self, client, seed_users,
                                           seed_employee, seed_project, app):
        """Allocation of exactly 100% is valid."""
        login(client, 'admin@test.com', 'Password123!')
        resp = client.post('/allocations/add', data={
            'employee_id': seed_employee,
            'project_id': seed_project,
            'assigned_role': 'Full-time Lead',
            'allocation_percentage': 100,
            'start_date': '2024-01-01',
            'end_date': '',
        }, follow_redirects=True)
        assert resp.status_code == 200
        with app.app_context():
            assert Allocation.query.count() == 1


class TestEmployeeValidation:

    def test_empty_full_name_rejected(self, client, seed_users):
        """Employee cannot be created without a full name."""
        login(client, 'admin@test.com', 'Password123!')
        resp = client.post('/employees/add', data={
            'employee_number': 'E100',
            'full_name': '',         # Missing required field
            'business_area': 'IT',
            'current_role': 'Dev',
            'grade': 'Analyst',
            'talent_segment': 'Core Performer',
            'readiness_level': 'Ready in 3+ Years',
            'flight_risk': 'Low',
        }, follow_redirects=True)
        # Form should be re-rendered with validation errors
        assert resp.status_code == 200
        assert b'Add Employee' in resp.data   # Still on the add page

    def test_empty_employee_number_rejected(self, client, seed_users):
        """Employee number is required."""
        login(client, 'admin@test.com', 'Password123!')
        resp = client.post('/employees/add', data={
            'employee_number': '',
            'full_name': 'John Doe',
            'business_area': 'IT',
            'current_role': 'Dev',
            'grade': 'Analyst',
            'talent_segment': 'Core Performer',
            'readiness_level': 'Ready in 3+ Years',
            'flight_risk': 'Low',
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b'Add Employee' in resp.data

    def test_invalid_grade_rejected(self, client, seed_users):
        """A grade value not in the controlled vocabulary is rejected."""
        login(client, 'admin@test.com', 'Password123!')
        resp = client.post('/employees/add', data={
            'employee_number': 'E200',
            'full_name': 'Jane Doe',
            'business_area': 'IT',
            'current_role': 'Dev',
            'grade': 'SuperAdmin',    # Not a valid choice
            'talent_segment': 'Core Performer',
            'readiness_level': 'Ready in 3+ Years',
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b'Add Employee' in resp.data


class TestSecurityValidation:

    def test_sql_injection_login_fails(self, client, seed_users):
        """
        SQL injection attempt in the login form does not authenticate.

    
        """
        resp = client.post('/login', data={
            'email': "' OR '1'='1",
            'password': "' OR '1'='1",
        }, follow_redirects=True)
        # must not be on the dashboard — injection has not worked
        assert b'Total Employees' not in resp.data
        # Must still be on the login page
        assert b'Log In' in resp.data

    def test_another_injection_attempt_fails(self, client, seed_users):
        """A UNION-based injection pattern in email is handled safely."""
        resp = client.post('/login', data={
            'email': "admin@test.com' UNION SELECT * FROM users--",
            'password': 'anything',
        }, follow_redirects=True)
        assert b'Total Employees' not in resp.data

    def test_protected_route_redirects_anonymous_user(self, client):
        """
        An anonymous (not logged in) user accessing a protected route
        is redirected to /login, not shown the page.
        """
        resp = client.get('/employees', follow_redirects=True)
        assert b'Log In' in resp.data
        assert b'Employees' not in resp.data or b'Log In' in resp.data

    def test_protected_admin_route_redirects_anonymous(self, client):
        """Anonymous user hitting /admin is redirected to login."""
        resp = client.get('/admin', follow_redirects=True)
        assert b'Log In' in resp.data

    def test_viewer_blocked_from_admin_url(self, client, seed_users):
        """
        OWASP A01 — Broken Access Control:
        A viewer who manually types /admin receives an access denied message,
        not the admin panel content.
        """
        login(client, 'viewer@test.com', 'Password123!')
        resp = client.get('/admin', follow_redirects=True)
        assert b'Access denied' in resp.data
        assert b'Admin Panel' not in resp.data

    def test_open_redirect_prevented(self, client, seed_users):
        """
        OWASP A01 — Open Redirect:
        The ?next= parameter must not redirect the user to an external URL.
        """
        login(client, 'admin@test.com', 'Password123!')
        # Try to abuse the next param to redirect to an external site
        resp = client.post(
            '/login?next=http://evil.com',
            data={'email': 'admin@test.com', 'password': 'Password123!'},
            follow_redirects=False
        )
        location = resp.headers.get('Location', '')
        assert 'evil.com' not in location

    def test_xss_in_employee_name_is_escaped(self, client, seed_users, app):
        """
        OWASP A03 — XSS (Cross-Site Scripting):
        User-supplied data containing HTML/JS tags must be escaped by Jinja2
        before being rendered, so the browser does not execute the script.
        """
        login(client, 'admin@test.com', 'Password123!')
        xss_payload = '<script>alert("xss")</script>'
        client.post('/employees/add', data={
            'employee_number': 'XSS01',
            'full_name': xss_payload,
            'business_area': 'Test',
            'current_role': 'Test',
            'grade': 'Analyst',
            'talent_segment': 'Core Performer',
            'readiness_level': 'Ready in 3+ Years',
            'flight_risk': 'Low',
            'future_role_aspiration': '',
        }, follow_redirects=True)
        # The employee list must not contain the raw script tag.

        resp = client.get('/employees')
        assert b'<script>alert' not in resp.data
        assert b'&lt;script&gt;' in resp.data

    def test_password_strength_enforced(self, client, seed_users):
        login(client, 'admin@test.com', 'Password123!')
        resp = client.post('/register', data={
            'username': 'weakuser',
            'email': 'weak@test.com',
            'password': 'password',        # no uppercase, no digit, no special char
            'confirm_password': 'password',
            'role': 'viewer',
            'business_area': '',
        }, follow_redirects=True)
        # Should stay on the register page with validation errors
        assert b'Register User' in resp.data
