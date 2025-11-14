# 🔗 URL Shortener

A modern URL shortening service built with Django. Transform long URLs into short, shareable links with analytics and custom aliases.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Django](https://img.shields.io/badge/django-5.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🌟 Features

-   ✂️ **Instant URL Shortening** - Convert long URLs to short links
-   🎨 **Custom Aliases** - Create memorable branded short codes
-   📊 **Analytics Dashboard** - Track clicks, referrers, and locations
-   📱 **QR Code Generation** - Automatic QR codes for every link
-   ⏰ **Link Expiration** - Set time-limited URLs
-   🔐 **User Authentication** - Manage your own links
-   🚀 **REST API** - Integrate with other applications

## 🛠️ Tech Stack

-   **Backend:** Django 5.0+
-   **Database:** PostgreSQL (Production)
-   **Cache:** Redis
-   **API:** Django REST Framework

## 🚀 Quick Start

### Prerequisites

-   Python 3.10+
-   pip

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/url-shortener.git
cd url-shortener

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

## 📧 Contact

Your Name - [@yourhandle](https://twitter.com/yourhandle)

Project Link: [https://github.com/yourusername/url-shortener](https://github.com/yourusername/url-shortener)

---

⭐ If you find this project useful, please consider giving it a star!
