"""
Django settings for UrlShortener project - Production settings.
"""

from config.settings.base import Base, env, BASE_DIR
from csp.constants import SELF


class Prod(Base):
    DEBUG = False

    ALLOWED_HOSTS = env("ALLOWED_HOSTS").split(",")

    # Production-specific settings
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"

    # Additional security headers (handled by SecurityMiddleware)
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Content Security Policy (CSP) via django-csp

    CONTENT_SECURITY_POLICY = {
        "DIRECTIVES": {
            "default-src": [SELF],
            "script-src": [SELF, "unsafe-inline"],
            "style-src": [SELF, "unsafe-inline"],
            "img-src": [SELF, "data:", "https:"],
            "font-src": [SELF, "https:"],
        }
    }
