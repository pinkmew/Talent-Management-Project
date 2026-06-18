# Fujitsu Talent Management Portal

A secure web application built with Python and Flask for managing employee talent, project allocations, and development actions within an internal automation team.

---

## Project Purpose

This portal replaces manual talent tracking in Microsoft tools (SharePoint, Power BI) with a proper database-backed web application. It provides structured CRUD functionality, role-based access control, dashboard visualisations, and a full audit trail — all with demonstrable OWASP security protections.

---

## Business Context

The Fujitsu Digital Automation team manages talent across multiple business areas and projects. Currently, talent review data is stored in disconnected spreadsheets and SharePoint lists with no access control, no audit trail, and no consistent validation. This portal centralises that data with proper security, role separation, and reporting.

---

## Features

| Feature | Description |
|---|---|
| Role-based login | Admin, Manager, Viewer roles with different permissions |
| Employee management | Full CRUD with talent segment and readiness tracking |
| Project management | Track projects, statuses, start/end dates |
| Allocations | Link employees to projects with percentage allocation |
| Talent reviews | Performance/potential ratings and development actions |
| Dashboard | KPI cards + 4 Chart.js visualisations |
| Audit log | Immutable record of all create/update/delete actions |
| Security | CSRF, hashed passwords, ORM queries, RBAC decorators |

---

## Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Framework | Flask 3 |
| ORM | Flask-SQLAlchemy |
| Authentication | Flask-Login |
| Forms / CSRF | Flask-WTF + WTForms |
| Password hashing | Werkzeug `generate_password_hash` |
| Database | SQLite (local) |
| Frontend | Bootstrap 5 + Bootstrap Icons |
| Charts | Chart.js 4 |
| Testing | pytest + pytest-flask |
| Deployment | Gunicorn + Render/Heroku |

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/talent-management-portal.git
cd talent-management-portal
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env and set a strong SECRET_KEY for production
```

### 5. Seed the database

```bash
python seed.py
```

### 6. Run the application

```bash
python run.py
```

Open your browser at: **http://127.0.0.1:5000**

---

## Test Accounts

| Role | Email | Password |
|---|---|---|
| Admin | admin@example.com | Password123! |
| Manager | manager@example.com | Password123! |
| Viewer | viewer@example.com | Password123! |

---

## Running Tests

```bash
pytest
```

To see verbose output:

```bash
pytest -v
```

To see coverage:

```bash
pip install pytest-cov
pytest --cov=app --cov-report=term-missing
```

---

## Project Structure

```
talent_management_portal/
├── app/
│   ├── __init__.py          # App factory, extensions
│   ├── models.py            # SQLAlchemy ORM models
│   ├── forms.py             # Flask-WTF form definitions
│   ├── utils.py             # RBAC decorators
│   ├── routes/
│   │   ├── auth.py          # Login / logout / register
│   │   ├── dashboard.py     # Dashboard + chart data API
│   │   ├── employees.py     # Employee CRUD
│   │   ├── projects.py      # Project CRUD
│   │   ├── allocations.py   # Allocation CRUD
│   │   ├── reviews.py       # Talent review CRUD
│   │   └── admin.py         # Admin panel + audit log
│   ├── templates/           # Jinja2 HTML templates
│   └── static/              # CSS + JS
├── tests/
│   ├── conftest.py          # Shared fixtures
│   ├── test_auth.py         # Authentication tests
│   ├── test_access_control.py  # RBAC tests
│   ├── test_crud.py         # CRUD tests
│   └── test_validation.py   # Validation + security tests
├── config.py                # Dev / Test / Production configs
├── run.py                   # Entry point
├── seed.py                  # Sample data
├── requirements.txt
└── Procfile                 # Gunicorn for deployment
```

---

## Security Features — OWASP Top 10 Mapping

### 1. A01 — Broken Access Control

**Implementation:** `app/utils.py` defines `@admin_required` and `@manager_required` decorators applied to every mutating route. Unauthenticated users are redirected to `/login` by Flask-Login. A viewer who manually navigates to `/admin` receives an "Access denied" flash message.

**Evidence to capture:** Screenshot showing a viewer being denied access to `/admin` and `/employees/add`.

### 2. A02 — Cryptographic Failures

**Implementation:** `app/models.py` — `User.set_password()` uses `werkzeug.security.generate_password_hash()`. Passwords are never stored or logged in plain text. The `SECRET_KEY` is loaded from an environment variable, never hard-coded.

**Evidence to capture:** Show the database record with `password_hash` field (a long bcrypt hash, not the original password). Show `.env.example` vs `.env`.

### 3. A03 — Injection (SQL Injection)

**Implementation:** All database queries in `app/routes/` use SQLAlchemy ORM methods (`User.query.filter_by(...)`, `.get_or_404()` etc.). No raw SQL strings are concatenated with user input anywhere in the codebase.

**Evidence to capture:** Screenshot of the test `test_sql_injection_login_fails` passing. Show the ORM query in `auth.py` vs what a vulnerable raw SQL version would look like.

### 4. A05 — Security Misconfiguration

**Implementation:** `SECRET_KEY` defaults to a dev value but production deployments must override it via environment variables. `DEBUG` is off in `ProductionConfig`. `.env` is in `.gitignore` and never committed.

### 5. A07 — Identification and Authentication Failures

**Implementation:** Generic error message on failed login ("Invalid email or password") prevents user enumeration. Passwords are hashed with Werkzeug. Session management is handled by Flask-Login's secure cookie.

### CSRF Protection (OWASP A01 / A05)

**Implementation:** `Flask-WTF CSRFProtect` is initialised in `app/__init__.py` and applies globally. Every form includes `{{ form.hidden_tag() }}` which renders the CSRF token. Forms that submit without a valid token are rejected with a 400 error.

**Evidence to capture:** Use browser devtools to remove the CSRF token field from a form submission and show the 400 response.

---

## Deployment Notes

### Render (recommended — free tier)

1. Push code to GitHub (ensure `.env` is NOT committed)
2. Create a new **Web Service** on [render.com](https://render.com)
3. Set build command: `pip install -r requirements.txt && python seed.py`
4. Set start command: `gunicorn run:app`
5. Add environment variable: `SECRET_KEY=<your-strong-key>`
6. Add environment variable: `FLASK_ENV=production`

### Heroku

```bash
heroku create your-app-name
heroku config:set SECRET_KEY=your-strong-key FLASK_ENV=production
git push heroku main
heroku run python seed.py
```

---

## Screenshots / Evidence Checklist

Collect these screenshots for your assessment report:

- [ ] Login page
- [ ] Dashboard with all 4 charts populated
- [ ] Employee list (all roles)
- [ ] Add Employee form with validation errors shown
- [ ] Employee detail page with allocations and reviews
- [ ] Admin panel overview
- [ ] Audit log page
- [ ] Viewer denied access to `/admin` (Access denied flash)
- [ ] Viewer denied access to `/employees/add`
- [ ] Failed login with generic error message
- [ ] SQLite database open in DB Browser showing `password_hash` (no plain text)
- [ ] pytest output showing all tests passing
- [ ] CSRF token in HTML source (browser devtools)
- [ ] `.gitignore` showing `.env` excluded
- [ ] GitHub repository showing clean commit history

---

## Database Schema

```
users          employees        projects
  id             id               id
  username       employee_number  project_name
  email          full_name        department
  password_hash  business_area    start_date
  role           current_role     end_date
  business_area  grade            status
  created_at     talent_segment
                 readiness_level
                 created_at

allocations      talent_reviews   audit_logs
  id               id               id
  employee_id FK   employee_id FK   user_id FK
  project_id FK    reviewed_by FK   action_type
  assigned_role    review_date      table_changed
  allocation_%     performance      record_id
  start_date       potential        description
  end_date         dev_action       timestamp
  created_at       status
                   created_at
```
