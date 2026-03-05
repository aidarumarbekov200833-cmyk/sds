# 🔍 UptimeWatch — Professional Site Monitoring Service

A full-stack Django monitoring service with Material Design UI, real-time status updates, ApexCharts analytics, and Celery-powered background checks.

## ✨ Features

- **Dashboard** — Live monitor cards with Online/Offline/Slow status, response times, uptime %
- **Monitoring Logic** — HTTP status checks + keyword search + response time measurement
- **Alert System** — Email & Telegram alert simulation on downtime/recovery
- **Charts** — Interactive ApexCharts: response time area chart + daily uptime bar chart
- **Status Page** — Public page with 90-day incident history (no auth required)
- **Live Updates** — Fetch API polling every 30s, no page reloads
- **Skeleton Loaders** — Smooth loading states for charts and stats
- **Responsive** — Mobile-friendly with collapsible sidebar

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run migrations
```bash
python manage.py migrate
```

### 3. Create admin user
```bash
python manage.py createsuperuser
```

### 4. Load demo data (optional)
```bash
python create_demo_data.py
```

### 5. Start the server
```bash
python manage.py runserver
```

Open: **http://127.0.0.1:8000/**

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 6+, Django REST Framework |
| Task Queue | Celery 5 + Redis |
| Frontend | HTML5, ES6+ JavaScript |
| UI | Material Design (custom CSS + Material Icons) |
| Charts | ApexCharts |
| Database | SQLite (dev) / PostgreSQL (prod) |

## 📋 URL Routes

| URL | Description |
|-----|-------------|
| `/` | Dashboard |
| `/monitor/add/` | Add new monitor |
| `/monitor/<id>/` | Monitor detail + charts |
| `/monitor/<id>/edit/` | Edit monitor |
| `/status/` | Public status page |
| `/admin/` | Django admin |
| `/api/stats/` | Dashboard stats API |
| `/api/monitors/` | Monitors list API |
| `/api/monitors/<id>/chart/response-time/` | Chart data API |
| `/api/monitors/<id>/chart/uptime/` | Uptime chart API |
| `/api/monitors/<id>/check-now/` | Trigger immediate check |

## ⚙️ Celery Setup (for real background checks)

Requires Redis running locally:

```bash
# Terminal 1: Redis (Docker)
docker run -p 6379:6379 redis:alpine

# Terminal 2: Celery worker
celery -A monitoring_service worker --loglevel=info

# Terminal 3: Celery beat (scheduler)
celery -A monitoring_service beat --loglevel=info
```

## 🔑 Admin Credentials (demo)
- URL: http://127.0.0.1:8000/admin/
- Username: `admin`
- Password: `admin123`

## 📁 Project Structure

```
fullstack gaming/
├── monitoring_service/     # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── celery.py
├── monitors/               # Main app
│   ├── models.py           # Monitor, CheckLog, Alert, Incident
│   ├── views.py            # Template + API views
│   ├── tasks.py            # Celery monitoring tasks
│   ├── serializers.py      # DRF serializers
│   ├── forms.py            # Django forms
│   ├── admin.py            # Admin config
│   └── urls.py             # URL patterns
├── templates/
│   ├── base.html           # Base layout with sidebar
│   └── monitors/           # All page templates
├── static/
│   ├── css/main.css        # Material Design styles
│   └── js/main.js          # Global JS utilities
├── create_demo_data.py     # Demo data script
└── requirements.txt
```
