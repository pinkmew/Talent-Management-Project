"""
app/routes/employees.py — Employee CRUD routes.


Audit log entries are written on every mutating action.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from datetime import datetime, timezone

from app import db
from app.models import Employee, AuditLog
from app.forms import EmployeeForm
from app.utils import admin_required, manager_required

employees_bp = Blueprint('employees', __name__)


@employees_bp.route('/employees')
@login_required
def index():
    """List all employees."""
    employees = Employee.query.order_by(Employee.full_name).all()
    return render_template('employees/index.html', employees=employees, title='Employees')


@employees_bp.route('/employees/<int:employee_id>')
@login_required
def detail(employee_id):
    """View a single employee's profile including allocations and reviews."""
    employee = Employee.query.get_or_404(employee_id)
    return render_template('employees/detail.html', employee=employee, title=employee.full_name)


@employees_bp.route('/employees/add', methods=['GET', 'POST'])
@login_required
@manager_required   # admin or manager only
def add():
    form = EmployeeForm()
    if form.validate_on_submit():
        # Check employee number uniqueness
        if Employee.query.filter_by(employee_number=form.employee_number.data).first():
            flash('That employee number is already in use.', 'danger')
            return render_template('employees/add.html', form=form, title='Add Employee')

        employee = Employee(
            employee_number=form.employee_number.data.strip(),
            full_name=form.full_name.data.strip(),
            business_area=form.business_area.data.strip(),
            current_role=form.current_role.data.strip(),
            grade=form.grade.data,
            talent_segment=form.talent_segment.data,
            future_role_aspiration=form.future_role_aspiration.data.strip(),
            readiness_level=form.readiness_level.data,
            flight_risk=form.flight_risk.data,
        )
        db.session.add(employee)
        db.session.flush()  # Gets the new ID before committing

        log = AuditLog(
            user_id=current_user.id,
            action_type='CREATE',
            table_changed='employees',
            record_id=employee.id,
            description=f'Created employee: {employee.full_name} ({employee.employee_number})'
        )
        db.session.add(log)
        db.session.commit()

        flash(f'Employee "{employee.full_name}" ({employee.employee_number}) added successfully.', 'success')
        return redirect(url_for('employees.index'))

    return render_template('employees/add.html', form=form, title='Add Employee')


@employees_bp.route('/employees/<int:employee_id>/edit', methods=['GET', 'POST'])
@login_required
@manager_required   # admin or manager only
def edit(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    form = EmployeeForm(obj=employee)

    if form.validate_on_submit():
        # Check uniqueness only if the number has changed
        if (form.employee_number.data != employee.employee_number and
                Employee.query.filter_by(employee_number=form.employee_number.data).first()):
            flash('That employee number is already in use.', 'danger')
            return render_template('employees/edit.html', form=form, employee=employee,
                                   title='Edit Employee')

        employee.employee_number       = form.employee_number.data.strip()
        employee.full_name             = form.full_name.data.strip()
        employee.business_area         = form.business_area.data.strip()
        employee.current_role          = form.current_role.data.strip()
        employee.grade                 = form.grade.data
        employee.talent_segment        = form.talent_segment.data
        employee.future_role_aspiration = form.future_role_aspiration.data.strip()
        employee.readiness_level       = form.readiness_level.data
        employee.flight_risk           = form.flight_risk.data
        employee.updated_at            = datetime.now(timezone.utc)

        log = AuditLog(
            user_id=current_user.id,
            action_type='UPDATE',
            table_changed='employees',
            record_id=employee.id,
            description=f'Updated employee: {employee.full_name} ({employee.employee_number})'
        )
        db.session.add(log)
        db.session.commit()

        flash(f'Employee "{employee.full_name}" updated successfully. Changes saved.', 'success')
        return redirect(url_for('employees.detail', employee_id=employee.id))

    return render_template('employees/edit.html', form=form, employee=employee,
                           title='Edit Employee')


@employees_bp.route('/employees/<int:employee_id>/delete', methods=['POST'])
@login_required
@admin_required   # admin only
def delete(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    name = employee.full_name

    log = AuditLog(
        user_id=current_user.id,
        action_type='DELETE',
        table_changed='employees',
        record_id=employee.id,
        description=f'Deleted employee: {name} ({employee.employee_number})'
    )
    db.session.add(log)
    db.session.delete(employee)
    db.session.commit()

    flash(f'Employee "{name}" has been permanently deleted.', 'success')
    return redirect(url_for('employees.index'))
