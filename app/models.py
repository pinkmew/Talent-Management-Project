"""
app/models.py — SQLAlchemy ORM models.

"""

from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


# User loader
def load_user(user_id: int):
    return User.query.get(int(user_id))



# User model

class User(UserMixin, db.Model):
    """
    Represents a portal user.
    """
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80),  unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    # role controls what actions the user can perform
    role          = db.Column(db.String(20),  nullable=False, default='viewer')
    business_area = db.Column(db.String(100), nullable=True)
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    reviews    = db.relationship('TalentReview', backref='reviewer', lazy=True,
                                 foreign_keys='TalentReview.reviewed_by')
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True)

    def set_password(self, password: str) -> None:
        """Hash and store the password.  Plain text is never persisted."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify a candidate password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    # Role-checking helpers
    def is_admin(self) -> bool:
        return self.role == 'admin'

    def is_manager(self) -> bool:
        return self.role in ('admin', 'manager')

    def __repr__(self) -> str:
        return f'<User {self.username} [{self.role}]>'


# Employee model

class Employee(db.Model):
    """Tracks talent within the organisation."""
    __tablename__ = 'employees'

    id                    = db.Column(db.Integer, primary_key=True)
    employee_number       = db.Column(db.String(20),  unique=True, nullable=False)
    full_name             = db.Column(db.String(120), nullable=False)
    business_area         = db.Column(db.String(100), nullable=False)
    current_role          = db.Column(db.String(100), nullable=False)
    grade                 = db.Column(db.String(20),  nullable=False)
    talent_segment        = db.Column(db.String(50),  nullable=False)
    future_role_aspiration = db.Column(db.String(100), nullable=True)
    readiness_level       = db.Column(db.String(50),  nullable=False)
    # Flight risk: likelihood the employee may leave the organisation (Low/Medium/High)
    flight_risk           = db.Column(db.String(20),  nullable=False, default='Low')
    created_at            = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at            = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                                      onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    allocations = db.relationship('Allocation',    backref='employee', lazy=True,
                                  cascade='all, delete-orphan')
    reviews     = db.relationship('TalentReview', backref='employee', lazy=True,
                                  cascade='all, delete-orphan',
                                  foreign_keys='TalentReview.employee_id')

    def __repr__(self) -> str:
        return f'<Employee {self.employee_number} – {self.full_name}>'



# Project model

class Project(db.Model):
    __tablename__ = 'projects'

    id           = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(150), nullable=False)
    department   = db.Column(db.String(100), nullable=False)
    start_date   = db.Column(db.Date, nullable=False)
    end_date     = db.Column(db.Date, nullable=True)
    status       = db.Column(db.String(30), nullable=False, default='Active')
    created_at   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                             onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    allocations = db.relationship('Allocation', backref='project', lazy=True,
                                  cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f'<Project {self.project_name}>'


# Allocation model

class Allocation(db.Model):
    """
    Links an Employee to a Project with a role and percentage allocation.
    
    """
    __tablename__ = 'allocations'

    id                    = db.Column(db.Integer, primary_key=True)
    # Foreign keys enforce referential integrity
    employee_id           = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    project_id            = db.Column(db.Integer, db.ForeignKey('projects.id'),  nullable=False)
    assigned_role         = db.Column(db.String(100), nullable=False)
    allocation_percentage = db.Column(db.Integer,     nullable=False)
    start_date            = db.Column(db.Date, nullable=False)
    end_date              = db.Column(db.Date, nullable=True)
    created_at            = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f'<Allocation emp={self.employee_id} proj={self.project_id} {self.allocation_percentage}%>'


# TalentReview model

class TalentReview(db.Model):
    """Records a performance/potential review and development action for an employee."""
    __tablename__ = 'talent_reviews'

    id                 = db.Column(db.Integer, primary_key=True)
    employee_id        = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    reviewed_by        = db.Column(db.Integer, db.ForeignKey('users.id'),     nullable=False)
    review_date        = db.Column(db.Date,    nullable=False)
    performance_rating = db.Column(db.String(20), nullable=False)
    potential_rating   = db.Column(db.String(20), nullable=False)
    development_action = db.Column(db.Text, nullable=True)
    status             = db.Column(db.String(20), nullable=False, default='Open')
    created_at         = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at         = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                                   onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f'<TalentReview emp={self.employee_id} [{self.status}]>'



# AuditLog model

class AuditLog(db.Model):
    """
    Immutable audit trail of all create/update/delete actions.
    """
    __tablename__ = 'audit_logs'

    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action_type   = db.Column(db.String(20),  nullable=False)   # CREATE, UPDATE, DELETE
    table_changed = db.Column(db.String(50),  nullable=False)
    record_id     = db.Column(db.Integer,     nullable=True)
    description   = db.Column(db.Text,        nullable=False)
    timestamp     = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f'<AuditLog {self.action_type} on {self.table_changed} by user={self.user_id}>'
