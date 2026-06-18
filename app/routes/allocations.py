"""
app/routes/allocations.py — Allocation CRUD routes.

Access control:
  - Viewing: all authenticated users
  - Add / Edit: admin or manager
  - Delete: admin only
"""

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models import Allocation, Employee, Project, AuditLog
from app.forms import AllocationForm
from app.utils import admin_required, manager_required

allocations_bp = Blueprint('allocations', __name__)


def _populate_form_choices(form):
    """Populate employee and project dropdowns from the database."""
    form.employee_id.choices = [
        (e.id, f'{e.full_name} ({e.employee_number})')
        for e in Employee.query.order_by(Employee.full_name).all()
    ]
    form.project_id.choices = [
        (p.id, p.project_name)
        for p in Project.query.filter_by(status='Active').order_by(Project.project_name).all()
    ]


@allocations_bp.route('/allocations')
@login_required
def index():
    allocations = (
        Allocation.query
        .join(Employee)
        .join(Project)
        .order_by(Employee.full_name)
        .all()
    )
    return render_template('allocations/index.html', allocations=allocations, title='Allocations')


@allocations_bp.route('/allocations/add', methods=['GET', 'POST'])
@login_required
@manager_required
def add():
    form = AllocationForm()
    _populate_form_choices(form)

    if form.validate_on_submit():
        allocation = Allocation(
            employee_id=form.employee_id.data,
            project_id=form.project_id.data,
            assigned_role=form.assigned_role.data.strip(),
            allocation_percentage=form.allocation_percentage.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
        )
        db.session.add(allocation)
        db.session.flush()

        emp  = db.session.get(Employee, allocation.employee_id)
        proj = db.session.get(Project, allocation.project_id)
        log  = AuditLog(
            user_id=current_user.id,
            action_type='CREATE',
            table_changed='allocations',
            record_id=allocation.id,
            description=f'Allocated {emp.full_name} to {proj.project_name} at {allocation.allocation_percentage}%'
        )
        db.session.add(log)
        db.session.commit()

        flash('Allocation created successfully.', 'success')
        return redirect(url_for('allocations.index'))

    return render_template('allocations/add.html', form=form, title='Add Allocation')


@allocations_bp.route('/allocations/<int:allocation_id>/edit', methods=['GET', 'POST'])
@login_required
@manager_required
def edit(allocation_id):
    allocation = Allocation.query.get_or_404(allocation_id)
    form = AllocationForm(obj=allocation)
    _populate_form_choices(form)

    if form.validate_on_submit():
        allocation.employee_id           = form.employee_id.data
        allocation.project_id            = form.project_id.data
        allocation.assigned_role         = form.assigned_role.data.strip()
        allocation.allocation_percentage = form.allocation_percentage.data
        allocation.start_date            = form.start_date.data
        allocation.end_date              = form.end_date.data

        log = AuditLog(
            user_id=current_user.id,
            action_type='UPDATE',
            table_changed='allocations',
            record_id=allocation.id,
            description=f'Updated allocation ID {allocation.id}'
        )
        db.session.add(log)
        db.session.commit()

        flash('Allocation updated successfully.', 'success')
        return redirect(url_for('allocations.index'))

    return render_template('allocations/edit.html', form=form, allocation=allocation,
                           title='Edit Allocation')


@allocations_bp.route('/allocations/<int:allocation_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(allocation_id):
    allocation = Allocation.query.get_or_404(allocation_id)

    log = AuditLog(
        user_id=current_user.id,
        action_type='DELETE',
        table_changed='allocations',
        record_id=allocation.id,
        description=f'Deleted allocation ID {allocation.id}'
    )
    db.session.add(log)
    db.session.delete(allocation)
    db.session.commit()

    flash('Allocation deleted.', 'success')
    return redirect(url_for('allocations.index'))
