"""
tests/test_access_control.py — Role-based access control tests.

"""

from tests.conftest import login


class TestUnauthenticatedAccess:

    def test_dashboard_requires_login(self, client, seed_users):
        """Unauthenticated GET /dashboard redirects to login."""
        resp = client.get('/dashboard', follow_redirects=True)
        assert b'Log In' in resp.data

    def test_employees_requires_login(self, client, seed_users):
        resp = client.get('/employees', follow_redirects=True)
        assert b'Log In' in resp.data

    def test_admin_panel_requires_login(self, client, seed_users):
        resp = client.get('/admin', follow_redirects=True)
        assert b'Log In' in resp.data

    def test_audit_log_requires_login(self, client, seed_users):
        resp = client.get('/admin/audit-log', follow_redirects=True)
        assert b'Log In' in resp.data


class TestViewerAccess:

    def test_viewer_can_see_employees(self, client, seed_users):
        """Viewer can read the employee list."""
        login(client, 'viewer@test.com', 'Password123!')
        resp = client.get('/employees', follow_redirects=True)
        assert resp.status_code == 200
        assert b'Employees' in resp.data

    def test_viewer_cannot_add_employee(self, client, seed_users):
        """Viewer is denied access to add employee form."""
        login(client, 'viewer@test.com', 'Password123!')
        resp = client.get('/employees/add', follow_redirects=True)
        # Should get access denied message
        assert b'Access denied' in resp.data

    def test_viewer_cannot_delete_employee(self, client, seed_users, seed_employee):
        """Viewer POST to delete endpoint is denied."""
        login(client, 'viewer@test.com', 'Password123!')
        resp = client.post(f'/employees/{seed_employee}/delete',
                           follow_redirects=True)
        assert b'Access denied' in resp.data

    def test_viewer_cannot_access_admin_panel(self, client, seed_users):
        """Viewer manually navigating to /admin is denied."""
        login(client, 'viewer@test.com', 'Password123!')
        resp = client.get('/admin', follow_redirects=True)
        assert b'Access denied' in resp.data

    def test_viewer_cannot_access_audit_log(self, client, seed_users):
        """Viewer cannot access the audit log."""
        login(client, 'viewer@test.com', 'Password123!')
        resp = client.get('/admin/audit-log', follow_redirects=True)
        assert b'Access denied' in resp.data

    def test_viewer_cannot_add_project(self, client, seed_users):
        """Viewer cannot access the add project page."""
        login(client, 'viewer@test.com', 'Password123!')
        resp = client.get('/projects/add', follow_redirects=True)
        assert b'Access denied' in resp.data


class TestManagerAccess:

    def test_manager_can_add_employee(self, client, seed_users):
        """Manager can access the add employee form."""
        login(client, 'manager@test.com', 'Password123!')
        resp = client.get('/employees/add', follow_redirects=True)
        assert resp.status_code == 200
        assert b'Add Employee' in resp.data

    def test_manager_cannot_delete_employee(self, client, seed_users, seed_employee):
        """Manager is denied the delete employee action."""
        login(client, 'manager@test.com', 'Password123!')
        resp = client.post(f'/employees/{seed_employee}/delete',
                           follow_redirects=True)
        assert b'Access denied' in resp.data

    def test_manager_cannot_access_admin_panel(self, client, seed_users):
        """Manager cannot access the admin panel."""
        login(client, 'manager@test.com', 'Password123!')
        resp = client.get('/admin', follow_redirects=True)
        assert b'Access denied' in resp.data

    def test_manager_cannot_add_project(self, client, seed_users):
        """Manager cannot add a project (admin-only)."""
        login(client, 'manager@test.com', 'Password123!')
        resp = client.get('/projects/add', follow_redirects=True)
        assert b'Access denied' in resp.data


class TestAdminAccess:

    def test_admin_can_access_admin_panel(self, client, seed_users):
        """Admin can access the admin panel."""
        login(client, 'admin@test.com', 'Password123!')
        resp = client.get('/admin', follow_redirects=True)
        assert resp.status_code == 200
        assert b'Admin Panel' in resp.data

    def test_admin_can_access_audit_log(self, client, seed_users):
        """Admin can access the full audit log."""
        login(client, 'admin@test.com', 'Password123!')
        resp = client.get('/admin/audit-log', follow_redirects=True)
        assert resp.status_code == 200
        assert b'Audit Log' in resp.data

    def test_admin_can_add_project(self, client, seed_users):
        """Admin can access the add project form."""
        login(client, 'admin@test.com', 'Password123!')
        resp = client.get('/projects/add', follow_redirects=True)
        assert resp.status_code == 200
        assert b'Add Project' in resp.data
