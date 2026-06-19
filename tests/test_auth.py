"""
tests/test_auth.py — Authentication tests.

"""

from tests.conftest import login, logout


class TestLogin:

    def test_valid_login_succeeds(self, client, seed_users):
        """A registered user with correct credentials reaches the dashboard."""
        resp = login(client, 'admin@test.com', 'Password123!')
        assert resp.status_code == 200
        # Dashboard content confirms successful login
        assert b'Dashboard' in resp.data

    def test_invalid_password_fails(self, client, seed_users):
        """Wrong password shows error and stays on login page."""
        resp = login(client, 'admin@test.com', 'WrongPassword!')
        assert resp.status_code == 200
        assert b'Invalid email or password' in resp.data
        # Shouldn't be on the dashboard
        assert b'Total Employees' not in resp.data

    def test_invalid_email_fails(self, client, seed_users):
        """Unregistered email shows the same generic error (no user enumeration)."""
        resp = login(client, 'nobody@test.com', 'Password123!')
        assert resp.status_code == 200
        assert b'Invalid email or password' in resp.data

    def test_logout_redirects_to_login(self, client, seed_users):
        """After logout the user ends up on the login page."""
        login(client, 'admin@test.com', 'Password123!')
        resp = logout(client)
        assert resp.status_code == 200
        assert b'Log In' in resp.data

    def test_manager_login_succeeds(self, client, seed_users):
        """Manager role user can log in successfully."""
        resp = login(client, 'manager@test.com', 'Password123!')
        assert resp.status_code == 200
        assert b'Dashboard' in resp.data

    def test_viewer_login_succeeds(self, client, seed_users):
        """Viewer role user can log in successfully."""
        resp = login(client, 'viewer@test.com', 'Password123!')
        assert resp.status_code == 200
        assert b'Dashboard' in resp.data

    def test_empty_credentials_fail(self, client, seed_users):
        """Submitting empty form fields shows validation errors."""
        resp = client.post('/login', data={'email': '', 'password': ''},
                           follow_redirects=True)
        assert resp.status_code == 200
        assert b'Log In' in resp.data
