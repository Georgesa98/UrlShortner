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

-   **Backend:** Django 5.2+
-   **Database:** PostgreSQL (Production) with optimized indexes
-   **Cache:** Redis with connection pooling
-   **API:** Django REST Framework
-   **Task Queue:** Celery with Redis broker
-   **Containerization:** Docker & Docker Compose

## 🚀 Quick Start

### Prerequisites

-   Python 3.11+
-   pip

### Installation

```bash
# Clone the repository
git clone https://github.com/Georgesa98/UrlShortner.git
cd UrlShortner

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver
```

Visit `http://localhost:8000` 🎉

## 🐳 Docker Setup

```bash
docker-compose up --build
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

---

⭐ If you find this project useful, please consider giving it a star!
