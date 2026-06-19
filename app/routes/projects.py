"""
app/routes/projects.py — Project CRUD routes.

"""

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timezone

from app import db
from app.models import Project, AuditLog
from app.forms import ProjectForm
from app.utils import admin_required

projects_bp = Blueprint('projects', __name__)


@projects_bp.route('/projects')
@login_required
def index():
    projects = Project.query.order_by(Project.project_name).all()
    return render_template('projects/index.html', projects=projects, title='Projects')


@projects_bp.route('/projects/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            project_name=form.project_name.data.strip(),
            department=form.department.data.strip(),
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            status=form.status.data,
        )
        db.session.add(project)
        db.session.flush()

        log = AuditLog(
            user_id=current_user.id,
            action_type='CREATE',
            table_changed='projects',
            record_id=project.id,
            description=f'Created project: {project.project_name}'
        )
        db.session.add(log)
        db.session.commit()

        flash(f'Project "{project.project_name}" created.', 'success')
        return redirect(url_for('projects.index'))

    return render_template('projects/add.html', form=form, title='Add Project')


@projects_bp.route('/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(project_id):
    project = Project.query.get_or_404(project_id)
    form = ProjectForm(obj=project)

    if form.validate_on_submit():
        project.project_name = form.project_name.data.strip()
        project.department   = form.department.data.strip()
        project.start_date   = form.start_date.data
        project.end_date     = form.end_date.data
        project.status       = form.status.data
        project.updated_at   = datetime.now(timezone.utc)

        log = AuditLog(
            user_id=current_user.id,
            action_type='UPDATE',
            table_changed='projects',
            record_id=project.id,
            description=f'Updated project: {project.project_name}'
        )
        db.session.add(log)
        db.session.commit()

        flash(f'Project "{project.project_name}" updated.', 'success')
        return redirect(url_for('projects.index'))

    return render_template('projects/edit.html', form=form, project=project, title='Edit Project')


@projects_bp.route('/projects/<int:project_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(project_id):
    project = Project.query.get_or_404(project_id)
    name = project.project_name

    log = AuditLog(
        user_id=current_user.id,
        action_type='DELETE',
        table_changed='projects',
        record_id=project.id,
        description=f'Deleted project: {name}'
    )
    db.session.add(log)
    db.session.delete(project)
    db.session.commit()

    flash(f'Project "{name}" deleted.', 'success')
    return redirect(url_for('projects.index'))
