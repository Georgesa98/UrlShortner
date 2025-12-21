"""
Django settings for UrlShortener project - Development settings.
"""

from config.settings.base import Base


class Dev(Base):
    DEBUG = True

    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]
