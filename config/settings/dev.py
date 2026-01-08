"""
Django settings for UrlShortener project - Development settings.
"""

from config.settings.base import Base


class Dev(Base):
    DEBUG = True

    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOW_CREDENTIALS = True

    CORS_ALLOW_METHODS = [
        "DELETE",
        "GET",
        "OPTIONS",
        "PATCH",
        "POST",
        "PUT",
    ]

    CORS_ALLOW_HEADERS = [
        "accept",
        "accept-encoding",
        "authorization",
        "content-type",
        "dnt",
        "origin",
        "user-agent",
        "x-csrftoken",
        "x-requested-with",
    ]
