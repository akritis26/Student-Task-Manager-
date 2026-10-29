# Student Task Manager

A responsive Django app for students to organize coursework, deadlines, and study tasks. Each account has a private task list with search, status and priority filters, quick completion, and profile editing. Django Admin remains available at `/admin/`.

## Requirements

- Python 3.12 or newer (Django 6.1 requires Python 3.12+)
- Django 6.1 (`pip install -r requirements.txt`)

## Run locally

From the project folder:

```bash
python3 -m venv venv
source venv/bin/activate       # macOS/Linux
# On Windows use: venv\Scripts\activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open <http://127.0.0.1:8000/> and create a student account. To use the admin panel, run `python manage.py createsuperuser` once and visit <http://127.0.0.1:8000/admin/>.

## Features

- Student registration, sign in, and sign out
- Personal dashboard with task totals and upcoming deadlines
- Add, edit, delete, and complete/reopen tasks
- Search by title, subject, or description; filter by status and priority
- Profile editing
- Per-user access enforced on every task query and mutation
- SQLite for simple local development

## Configuration

SQLite is used by default. Set `DJANGO_SECRET_KEY` to a private value before deploying, set `DJANGO_DEBUG=0`, and configure `DJANGO_ALLOWED_HOSTS` as a comma-separated list of hostnames. Never commit production secrets or the local SQLite database.

Bootstrap and Google Fonts are loaded from their public CDNs in the page templates.
