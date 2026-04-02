# BandaFlow — Kiosk Management System

A modern, elegant web application for managing kiosk suppliers, transactions, and balances.

---

## Tech Stack
- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python 3.10+, Django 4.2
- **Database:** PostgreSQL (Neon hosted)

---

## Project Structure

```
bandaflow/
├── bandaflow/            # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── kiosk/                # Main app
│   ├── migrations/
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/utils.js
│   ├── templates/kiosk/
│   │   ├── base.html
│   │   ├── index.html       ← Login page (root URL)
│   │   ├── signup.html
│   │   ├── forgot_password.html
│   │   ├── dashboard.html
│   │   ├── suppliers.html
│   │   ├── transactions.html
│   │   ├── balances.html
│   │   ├── admin_panel.html
│   │   └── 403.html
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── apps.py
├── manage.py
└── requirements.txt
```

---

## Setup Instructions

### 1. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run database migrations
```bash
python manage.py migrate
```

### 4. Create your first Admin user
```bash
python manage.py shell
```
Then in the shell:
```python
from kiosk.models import User
u = User.objects.create_superuser(username='admin', password='yourpassword')
u.role = 'admin'
u.save()
exit()
```

### 5. Collect static files (for deployment)
```bash
python manage.py collectstatic --noinput
```

### 6. Run the development server
```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000/** — this opens the Login page (index.html).

---

## Deployment Notes
- The login page is served at `/` which maps to `index.html` — no redirect issues on deploy.
- `whitenoise` handles static files in production.
- Database is hosted on Neon (PostgreSQL) — no local DB setup needed.
- Set `DEBUG = False` and update `SECRET_KEY` for production.

---

## User Roles
| Role    | Dashboard | Suppliers | Transactions | Balances | Admin Panel |
|---------|-----------|-----------|--------------|----------|-------------|
| Manager | ✓         | ✓         | ✓            | ✓        | ✗           |
| Admin   | ✓         | ✓         | ✓            | ✓        | ✓           |
