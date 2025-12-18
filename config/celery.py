import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

CELERY_BEAT_SCHEDUAL = {
    "deactivate-expired-urls-daily": {
        "task": "api.url.tasks.deactivate_expired_urls_task",
        "schedule": crontab(hour=0, minute=0),
        "kwargs": {"delete": False},
    },
    "maintain-shortcode-pool": {
        "task": "api.url.tasks.maintain_shortcode_pool",
        "schedule": crontab(minute="*/10"),
    },
    "process-analytics-buffer": {
        "task": "api.url.tasks.process_analytics_buffer",
        "schedule": 30.0,
    },
}

if __name__ == "__main__":
    app.start()
