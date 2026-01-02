import environ
from config.settings.base import Base
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DATABASE_NAME=(str),
    DATABASE_USER=(str),
    DATABASE_PASSWORD=(str),
    DATABASE_PORT=(str),
)
try:
    environ.Env.read_env(str(BASE_DIR / ".env"))
except FileNotFoundError:
    print("Warning: .env file not found. Using environment variables directly.")


class FrontendDev(Base):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "urlshortener_front",
            "USER": env("DATABASE_USER"),
            "PASSWORD": env("DATABASE_PASSWORD"),
            "HOST": env("DATABASE_HOST"),
            "PORT": env("DATABASE_PORT"),
        }
    }
