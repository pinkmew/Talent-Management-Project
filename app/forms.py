"""
app/forms.py — Flask-WTF form definitions.
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SelectField, TextAreaField,
    IntegerField, DateField, SubmitField
)
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, NumberRange,
    Optional, ValidationError
)


TALENT_SEGMENT_CHOICES = [
    ('', '-- Select --'),
    ('High Potential', 'High Potential'),
    ('Strong Performer', 'Strong Performer'),
    ('Core Performer', 'Core Performer'),
    ('Developing', 'Developing'),
    ('At Risk', 'At Risk'),
]

READINESS_CHOICES = [
    ('', '-- Select --'),
    ('Ready Now', 'Ready Now'),
    ('Ready in 1-2 Years', 'Ready in 1-2 Years'),
    ('Ready in 3+ Years', 'Ready in 3+ Years'),
    ('Not Applicable', 'Not Applicable'),
]

GRADE_CHOICES = [
    ('', '-- Select --'),
    ('Analyst', 'Analyst'),
    ('Consultant', 'Consultant'),
    ('Senior Consultant', 'Senior Consultant'),
    ('Manager', 'Manager'),
    ('Senior Manager', 'Senior Manager'),
    ('Director', 'Director'),
    ('Executive Director', 'Executive Director'),
]

PROJECT_STATUS_CHOICES = [
    ('Active', 'Active'),
    ('On Hold', 'On Hold'),
    ('Completed', 'Completed'),
    ('Cancelled', 'Cancelled'),
]

PERFORMANCE_RATING_CHOICES = [
    ('', '-- Select --'),
    ('Exceptional', 'Exceptional'),
    ('Exceeds Expectations', 'Exceeds Expectations'),
    ('Meets Expectations', 'Meets Expectations'),
    ('Below Expectations', 'Below Expectations'),
    ('Unsatisfactory', 'Unsatisfactory'),
]

POTENTIAL_RATING_CHOICES = [
    ('', '-- Select --'),
    ('High', 'High'),
    ('Medium', 'Medium'),
    ('Low', 'Low'),
]

REVIEW_STATUS_CHOICES = [
    ('Open', 'Open'),
    ('In Progress', 'In Progress'),
    ('Complete', 'Complete'),
]

FLIGHT_RISK_CHOICES = [
    ('', '-- Select --'),
    ('Low', 'Low — unlikely to leave'),
    ('Medium', 'Medium — some indicators present'),
    ('High', 'High — active risk of departure'),
]

ROLE_CHOICES = [
    ('viewer', 'Viewer'),
    ('manager', 'Manager'),
    ('admin', 'Admin'),
]


# Authentication forms


class LoginForm(FlaskForm):
    """Login — email + password."""
    email    = StringField('Email Address', validators=[
        DataRequired(message='Please enter your email address.'),
        Email(message='That does not look like a valid email address (e.g. user@example.com).')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Please enter your password.')
    ])
    submit   = SubmitField('Log In')


class RegisterForm(FlaskForm):
    """User registration — admin use only."""
    username      = StringField('Username', validators=[
        DataRequired(message='Username is required.'),
        Length(min=3, max=80, message='Username must be between 3 and 80 characters.')
    ])
    email         = StringField('Email', validators=[
        DataRequired(message='Email is required.'),
        Email(message='Please enter a valid email address (e.g. user@example.com).')
    ])
    password      = PasswordField('Password', validators=[
        DataRequired(message='Password is required.'),
        Length(min=8, message='Password must be at least 8 characters.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password.'),
        EqualTo('password', message='Passwords do not match — please re-enter.')
    ])
    role          = SelectField('Role', choices=ROLE_CHOICES, validators=[DataRequired()])
    business_area = StringField('Business Area', validators=[Optional(), Length(max=100)])
    submit        = SubmitField('Create User')

    def validate_password(self, field):
        """
        SECURITY — Weak Passwords (OWASP A07: Identification & Auth Failures):
        Enforce complexity so that passwords cannot be trivially guessed.
        Requires at least one uppercase letter, one digit, and one special character.
        """
        p = field.data or ''
        if not any(c.isupper() for c in p):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not any(c.isdigit() for c in p):
            raise ValidationError('Password must contain at least one number (0–9).')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in p):
            raise ValidationError('Password must contain at least one special character (e.g. ! @ # $).')


# Employee forms


class EmployeeForm(FlaskForm):
    """Add / Edit an employee record."""
    employee_number        = StringField('Employee Number', validators=[
        DataRequired(message='Employee number is required.'),
        Length(max=20)
    ])
    full_name              = StringField('Full Name', validators=[
        DataRequired(message='Full name is required.'),
        Length(max=120)
    ])
    business_area          = StringField('Business Area', validators=[
        DataRequired(message='Business area is required.'),
        Length(max=100)
    ])
    current_role           = StringField('Current Role', validators=[
        DataRequired(message='Current role is required.'),
        Length(max=100)
    ])
    grade                  = SelectField('Grade', choices=GRADE_CHOICES, validators=[
        DataRequired(message='Please select a grade.')
    ])
    talent_segment         = SelectField('Talent Segment', choices=TALENT_SEGMENT_CHOICES,
                                         validators=[DataRequired(message='Please select a talent segment.')])
    future_role_aspiration = StringField('Future Role Aspiration', validators=[
        Optional(), Length(max=100)
    ])
    readiness_level        = SelectField('Readiness Level', choices=READINESS_CHOICES,
                                          validators=[DataRequired(message='Please select a readiness level.')])
    flight_risk            = SelectField('Flight Risk', choices=FLIGHT_RISK_CHOICES,
                                         validators=[DataRequired(message='Please select a flight risk level.')])
    submit                 = SubmitField('Save Employee')



# Project forms


class ProjectForm(FlaskForm):
    """Add / Edit a project."""
    project_name = StringField('Project Name', validators=[
        DataRequired(message='Project name is required.'),
        Length(max=150)
    ])
    department   = StringField('Department', validators=[
        DataRequired(message='Department is required.'),
        Length(max=100)
    ])
    start_date   = DateField('Start Date', validators=[
        DataRequired(message='Start date is required.')
    ])
    end_date     = DateField('End Date', validators=[Optional()])
    status       = SelectField('Status', choices=PROJECT_STATUS_CHOICES,
                               validators=[DataRequired()])
    submit       = SubmitField('Save Project')

    def validate_end_date(self, field):
        """End date must be after start date when provided."""
        if field.data and self.start_date.data and field.data < self.start_date.data:
            raise ValidationError('End date must be on or after the start date.')



# Allocation forms


class AllocationForm(FlaskForm):
    """Assign an employee to a project."""
    employee_id           = SelectField('Employee', coerce=int, validators=[
        DataRequired(message='Please select an employee.')
    ])
    project_id            = SelectField('Project', coerce=int, validators=[
        DataRequired(message='Please select a project.')
    ])
    assigned_role         = StringField('Assigned Role', validators=[
        DataRequired(message='Assigned role is required.'),
        Length(max=100)
    ])
    # allocation percentage must be 0–100.
    allocation_percentage = IntegerField('Allocation %', validators=[
        DataRequired(message='Allocation percentage is required.'),
        NumberRange(min=0, max=100,
                    message='Allocation percentage must be between 0 and 100.')
    ])
    start_date            = DateField('Start Date', validators=[
        DataRequired(message='Start date is required.')
    ])
    end_date              = DateField('End Date', validators=[Optional()])
    submit                = SubmitField('Save Allocation')

    def validate_end_date(self, field):
        if field.data and self.start_date.data and field.data < self.start_date.data:
            raise ValidationError('End date must be on or after the start date.')


# Talent Review forms

class TalentReviewForm(FlaskForm):
    """Create / Edit a talent review."""
    review_date        = DateField('Review Date', validators=[
        DataRequired(message='Review date is required.')
    ])
    performance_rating = SelectField('Performance Rating',
                                     choices=PERFORMANCE_RATING_CHOICES,
                                     validators=[DataRequired(message='Please select a performance rating.')])
    potential_rating   = SelectField('Potential Rating',
                                     choices=POTENTIAL_RATING_CHOICES,
                                     validators=[DataRequired(message='Please select a potential rating.')])
    development_action = TextAreaField('Development Action', validators=[Optional()])
    status             = SelectField('Status', choices=REVIEW_STATUS_CHOICES,
                                     validators=[DataRequired()])
    submit             = SubmitField('Save Review')
