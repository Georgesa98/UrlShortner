# 🔗 URL Shortener

A modern URL shortening service built with Django. Transform long URLs into short, shareable links with analytics and custom aliases.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Django](https://img.shields.io/badge/django-5.2+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🌟 Features

-   ✂️ **Instant URL Shortening** - Convert long URLs to short links
-   🎨 **Custom Aliases** - Create memorable branded short codes
-   📊 **Analytics Dashboard** - Track clicks, referrers, and locations with Redis buffering for high performance
-   📱 **QR Code Generation** - Automatic QR codes for every link
-   ⏰ **Link Expiration** - Set time-limited URLs with automated cleanup
-   🔐 **User Authentication** - Manage your own links with role-based permissions
-   🚀 **REST API** - Integrate with other applications
-   🛡️ **Fraud Detection** - Advanced fraud detection and prevention system
-   🔄 **Redirection Rules** - Priority-based redirection rules for advanced URL management
-   📈 **Insight Analytics** - Comprehensive insights and reporting
-   🔍 **Audit System** - Full audit logging for security and compliance
-   ⚙️ **System Configuration** - Centralized system settings management
-   🐰 **Background Tasks** - Celery-powered asynchronous processing

## 🛠️ Tech Stack

-   **Backend:** Django 5.2+ with Django REST Framework
-   **Frontend:** Next.js 16.1+ with React 19
-   **Database:** PostgreSQL (Production) with optimized indexes
-   **Cache:** Redis with connection pooling
-   **Task Queue:** Celery with Redis broker
-   **Package Manager:** Bun (recommended) or npm
-   **Containerization:** Docker & Docker Compose

## 🚀 Quick Start

### Prerequisites

-   **Python 3.8+** (3.11+ recommended)
-   **PostgreSQL** - Running on port 5432
-   **Redis** - Running on port 6379
-   **Bun** or **Node.js + npm** - For frontend

### Automated Setup (Recommended)

Our cross-platform Python scripts work on **Windows, Linux, and macOS**:

```bash
# 1. Clone the repository
git clone https://github.com/Georgesa98/UrlShortner.git
cd UrlShortner

# 2. Ensure PostgreSQL and Redis are running
# Windows: Start services from Services panel (services.msc)
# Linux: sudo systemctl start postgresql redis

# 3. Run one-time setup
python setup.py

# 4. Start all services (Django + Celery + Frontend)
python run.py
```

That's it! The scripts will:
- ✅ Check all dependencies
- ✅ Create virtual environment
- ✅ Install Python packages
- ✅ Install frontend dependencies
- ✅ Run database migrations
- ✅ Seed test data
- ✅ Start all services automatically

**Access the application:**
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- Admin Panel: `http://localhost:3000/admin`

**Default credentials:**
- Username: `admin_tester`
- Password: `Password123!`

**To stop all services:**

```bash
python stop.py
```

Or press `Ctrl+C` in the terminal running `run.py`

### Manual Setup (Alternative)

<details>
<summary>Click to expand manual installation steps</summary>

```bash
# Clone the repository
git clone https://github.com/Georgesa98/UrlShortner.git
cd UrlShortner

# Backend setup
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your database credentials

# Database setup
python manage.py migrate
python manage.py seed_data --users 5 --urls-per-user 20

# Frontend setup
cd frontend
bun install  # or: npm install
cd ..

# Start services manually (in separate terminals)
# Terminal 1: Django
python manage.py runserver

# Terminal 2: Celery Worker
celery -A config worker --loglevel=info

# Terminal 3: Celery Beat
celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler

# Terminal 4: Frontend
cd frontend && bun run dev  # or: npm run dev
```

</details>

## 🐳 Docker Setup (Alternative)

```bash
# Start all services with Docker
docker-compose up --build

# Access at http://localhost:8000
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

---

⭐ If you find this project useful, please consider giving it a star!
