from datetime import date, datetime, timezone
from app.models import User, Employee, Project, Allocation, TalentReview, AuditLog


def seed_demo_data(db):
    admin = User(username='admin', email='admin@example.com',
                 role='admin', business_area='Digital Automation')
    admin.set_password('Password123!')
    manager = User(username='manager', email='manager@example.com',
                   role='manager', business_area='Application Services')
    manager.set_password('Password123!')
    viewer = User(username='viewer', email='viewer@example.com',
                  role='viewer', business_area='Infrastructure')
    viewer.set_password('Password123!')
    db.session.add_all([admin, manager, viewer])
    db.session.commit()

    employees_data = [
        ('FJ001', 'Alice Pemberton',  'Digital Automation',   'RPA Developer',        'Senior Consultant', 'High Potential',   'Automation Lead',   'Ready in 1-2 Years', 'Low'),
        ('FJ002', 'Ben Okafor',       'Application Services', 'Java Developer',        'Consultant',        'Strong Performer', 'Senior Developer',  'Ready in 1-2 Years', 'Medium'),
        ('FJ003', 'Chloe Watanabe',   'Infrastructure',       'Cloud Engineer',        'Manager',           'High Potential',   'Cloud Architect',   'Ready Now',          'Low'),
        ('FJ004', 'David Singh',      'Digital Automation',   'Business Analyst',      'Analyst',           'Core Performer',   'Senior BA',         'Ready in 3+ Years',  'Low'),
        ('FJ005', 'Elena Marchetti',  'Cybersecurity',        'Security Analyst',      'Senior Consultant', 'Strong Performer', 'Security Manager',  'Ready in 1-2 Years', 'Medium'),
        ('FJ006', 'Finn McCarthy',    'Application Services', 'Python Developer',      'Consultant',        'Developing',       'Senior Developer',  'Ready in 3+ Years',  'High'),
        ('FJ007', 'Grace Osei',       'Data & Analytics',     'Data Engineer',         'Senior Consultant', 'High Potential',   'Data Architect',    'Ready in 1-2 Years', 'Low'),
        ('FJ008', 'Hamid Reza',       'Infrastructure',       'DevOps Engineer',       'Manager',           'Strong Performer', 'Head of DevOps',    'Ready in 1-2 Years', 'Medium'),
        ('FJ009', 'Isla Drummond',    'Digital Automation',   'Automation Tester',     'Analyst',           'Core Performer',   'Senior Tester',     'Ready in 3+ Years',  'Low'),
        ('FJ010', 'James Adeyemi',    'Data & Analytics',     'Machine Learning Eng',  'Senior Consultant', 'At Risk',          'Not Applicable',    'Not Applicable',     'High'),
    ]
    employees = []
    for num, name, area, role, grade, segment, aspiration, readiness, risk in employees_data:
        e = Employee(employee_number=num, full_name=name, business_area=area,
                     current_role=role, grade=grade, talent_segment=segment,
                     future_role_aspiration=aspiration, readiness_level=readiness,
                     flight_risk=risk)
        db.session.add(e)
        employees.append(e)
    db.session.commit()

    projects_data = [
        ('RPA Process Automation',  'Digital Automation', date(2024, 1, 15), date(2024, 12, 31), 'Active'),
        ('Cloud Migration Wave 2',  'Infrastructure',     date(2024, 3, 1),  date(2025, 6, 30),  'Active'),
        ('Data Warehouse Rebuild',  'Data & Analytics',   date(2023, 9, 1),  date(2024, 8, 31),  'Completed'),
        ('Security Posture Review', 'Cybersecurity',      date(2024, 6, 1),  None,               'Active'),
    ]
    projects = []
    for name, dept, start, end, status in projects_data:
        p = Project(project_name=name, department=dept,
                    start_date=start, end_date=end, status=status)
        db.session.add(p)
        projects.append(p)
    db.session.commit()

    emp  = {e.employee_number: e for e in employees}
    proj = {p.project_name: p for p in projects}

    alloc_data = [
        (emp['FJ001'], proj['RPA Process Automation'],  'Lead Developer',    80,  date(2024, 1, 15), date(2024, 12, 31)),
        (emp['FJ002'], proj['Cloud Migration Wave 2'],  'Backend Developer', 60,  date(2024, 3, 1),  date(2025, 6, 30)),
        (emp['FJ003'], proj['Cloud Migration Wave 2'],  'Cloud Architect',   100, date(2024, 3, 1),  date(2025, 6, 30)),
        (emp['FJ004'], proj['RPA Process Automation'],  'Business Analyst',  50,  date(2024, 1, 15), date(2024, 12, 31)),
        (emp['FJ005'], proj['Security Posture Review'], 'Lead Security Eng', 100, date(2024, 6, 1),  None),
        (emp['FJ006'], proj['RPA Process Automation'],  'Python Developer',  80,  date(2024, 2, 1),  date(2024, 12, 31)),
        (emp['FJ006'], proj['Cloud Migration Wave 2'],  'Python Support',    60,  date(2024, 4, 1),  date(2024, 12, 31)),
        (emp['FJ007'], proj['Data Warehouse Rebuild'],  'Data Engineer',     80,  date(2023, 9, 1),  date(2024, 8, 31)),
        (emp['FJ008'], proj['Cloud Migration Wave 2'],  'DevOps Lead',       70,  date(2024, 3, 1),  date(2025, 6, 30)),
    ]
    for e, p, role, pct, start, end in alloc_data:
        db.session.add(Allocation(employee_id=e.id, project_id=p.id,
                                  assigned_role=role, allocation_percentage=pct,
                                  start_date=start, end_date=end))
    db.session.commit()

    review_data = [
        (emp['FJ001'], admin.id,   date(2024, 3, 15), 'Exceptional',          'High',   'Complete development plan for Automation Lead role.', 'In Progress'),
        (emp['FJ003'], admin.id,   date(2024, 4, 20), 'Exceeds Expectations', 'High',   'Complete AWS Solutions Architect Professional certification by Q3 2024.', 'Open'),
        (emp['FJ005'], manager.id, date(2024, 5, 10), 'Exceeds Expectations', 'Medium', 'Shadow CISO meetings and take ownership of one security initiative.', 'Open'),
        (emp['FJ007'], admin.id,   date(2024, 2, 28), 'Exceptional',          'High',   'Complete Google Professional Data Engineer exam.', 'In Progress'),
        (emp['FJ010'], manager.id, date(2024, 6, 5),  'Below Expectations',   'Low',    'Performance Improvement Plan initiated. Weekly check-ins with line manager.', 'Open'),
        (emp['FJ006'], manager.id, date(2024, 3, 1),  'Meets Expectations',   'Medium', 'Increase Python proficiency. Target senior developer badge within 18 months.', 'Complete'),
    ]
    for e, reviewer, rdate, perf, pot, action, status in review_data:
        db.session.add(TalentReview(employee_id=e.id, reviewed_by=reviewer,
                                    review_date=rdate, performance_rating=perf,
                                    potential_rating=pot, development_action=action,
                                    status=status))
    db.session.commit()

    audit_entries = [
        (admin.id,   'CREATE', 'employees',      emp['FJ001'].id, 'Seeded employee Alice Pemberton (FJ001)'),
        (admin.id,   'CREATE', 'projects',       proj['RPA Process Automation'].id, 'Seeded project: RPA Process Automation'),
        (admin.id,   'CREATE', 'projects',       proj['Cloud Migration Wave 2'].id,  'Seeded project: Cloud Migration Wave 2'),
        (manager.id, 'CREATE', 'talent_reviews', None, 'Seeded talent review for James Adeyemi'),
        (admin.id,   'UPDATE', 'employees',      emp['FJ010'].id, 'Talent segment updated to At Risk for James Adeyemi'),
        (manager.id, 'UPDATE', 'talent_reviews', None, 'Review for Finn McCarthy marked Complete'),
    ]
    for uid, action, table, rid, desc in audit_entries:
        db.session.add(AuditLog(user_id=uid, action_type=action, table_changed=table,
                                record_id=rid, description=desc))
    db.session.commit()
