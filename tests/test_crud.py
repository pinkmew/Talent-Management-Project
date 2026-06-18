"""
tests/test_crud.py — CRUD operation tests.

Verifies that create, read, update, and delete operations work correctly
for employees, projects, and allocations when called by an admin user.
"""

from datetime import date
from tests.conftest import login
from app import db
from app.models import Employee, Project, Allocation


class TestEmployeeCRUD:

    def test_admin_can_add_employee(self, client, seed_users, app):
        """Admin can POST a new employee and it appears in the database."""
        login(client, 'admin@test.com', 'Password123!')
        resp = client.post('/employees/add', data={
            'employee_number': 'E999',
            'full_name': 'New Person',
            'business_area': 'Test Area',
            'current_role': 'Developer',
            'grade': 'Analyst',
            'talent_segment': 'Core Performer',
            'readiness_level': 'Ready in 3+ Years',
            'flight_risk': 'Low',
            'future_role_aspiration': '',
        }, follow_redirects=True)
        assert resp.status_code == 200
        with app.app_context():
            emp = Employee.query.filter_by(employee_number='E999').first()
            assert emp is not None
            assert emp.full_name == 'New Person'

    def test_admin_can_edit_employee(self, client, seed_users, seed_employee, app):
        """Admin can update an employee's details."""
        login(client, 'admin@test.com', 'Password123!')
        resp = client.post(f'/employees/{seed_employee}/edit', data={
            'employee_number': 'T001',
            'full_name': 'Updated Name',
            'business_area': 'Updated Area',
            'current_role': 'Updated Role',
            'grade': 'Consultant',
            'talent_segment': 'Strong Performer',
            'readiness_level': 'Ready Now',
            'flight_risk': 'Medium',
            'future_role_aspiration': 'Manager',
        }, follow_redirects=True)
        assert resp.status_code == 200
        with app.app_context():
            emp = db.session.get(Employee, seed_employee)
            assert emp.full_name == 'Updated Name'
            assert emp.grade == 'Consultant'

    def test_admin_can_delete_employee(self, client, seed_users, seed_employee, app):
        """Admin can delete an employee; they no longer exist in the database."""
        login(client, 'admin@test.com', 'Password123!')
        resp = client.post(f'/employees/{seed_employee}/delete',
                           follow_redirects=True)
        assert resp.status_code == 200
        with app.app_context():
            emp = db.session.get(Employee, seed_employee)
            assert emp is None

    def test_employee_list_is_visible(self, client, seed_users, seed_employee):
        """All users can view the employee list."""
        login(client, 'viewer@test.com', 'Password123!')
        resp = client.get('/employees')
        assert resp.status_code == 200
        assert b'Employees' in resp.data


class TestProjectCRUD:

    def test_admin_can_add_project(self, client, seed_users, app):
        """Admin can create a new project."""
        login(client, 'admin@test.com', 'Password123!')
        resp = client.post('/projects/add', data={
            'project_name': 'New Test Project',
            'department': 'IT',
            'start_date': '2024-01-01',
            'end_date': '',
            'status': 'Active',
        }, follow_redirects=True)
        assert resp.status_code == 200
        with app.app_context():
            proj = Project.query.filter_by(project_name='New Test Project').first()
            assert proj is not None

    def test_admin_can_edit_project(self, client, seed_users, seed_project, app):
        """Admin can update a project's details."""
        login(client, 'admin@test.com', 'Password123!')
        resp = client.post(f'/projects/{seed_project}/edit', data={
            'project_name': 'Renamed Project',
            'department': 'Updated Dept',
            'start_date': '2024-01-01',
            'end_date': '',
            'status': 'On Hold',
        }, follow_redirects=True)
        assert resp.status_code == 200
        with app.app_context():
            proj = db.session.get(Project, seed_project)
            assert proj.project_name == 'Renamed Project'
            assert proj.status == 'On Hold'

    def test_admin_can_delete_project(self, client, seed_users, seed_project, app):
        """Admin can delete a project."""
        login(client, 'admin@test.com', 'Password123!')
        resp = client.post(f'/projects/{seed_project}/delete',
                           follow_redirects=True)
        assert resp.status_code == 200
        with app.app_context():
            proj = db.session.get(Project, seed_project)
            assert proj is None


class TestAllocationCRUD:

    def test_admin_can_create_allocation(self, client, seed_users,
                                         seed_employee, seed_project, app):
        """Admin can create a valid allocation linking an employee to a project."""
        login(client, 'admin@test.com', 'Password123!')
        resp = client.post('/allocations/add', data={
            'employee_id': seed_employee,
            'project_id': seed_project,
            'assigned_role': 'Lead Developer',
            'allocation_percentage': 80,
            'start_date': '2024-01-01',
            'end_date': '',
        }, follow_redirects=True)
        assert resp.status_code == 200
        with app.app_context():
            alloc = Allocation.query.filter_by(
                employee_id=seed_employee, project_id=seed_project
            ).first()
            assert alloc is not None
            assert alloc.allocation_percentage == 80
