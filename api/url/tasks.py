import json
import redis

from api.analytics.models import Visit
from api.url.services.ShortCodeService import ShortCodeService
from config.celery import app
from datetime import datetime, timezone
from api.url.models import Url
from django.conf import settings
from django.core.management import call_command


@app.task()
def deactivate_expired_urls_task():
    try:
        total_expired_urls_before = Url.objects.filter(
            expiration_date__lte=datetime.now(timezone.utc)
        ).count()
        total_urls_before = Url.objects.filter(is_active=True).count()
        call_command("deactivate_expired_urls", delete=False)
        total_urls_after = Url.objects.filter(is_active=True).count()
        cleaned_count = total_urls_before - total_urls_after
        return {
            "status": "success",
            "cleaned_count": cleaned_count,
            "expired_count_before": total_expired_urls_before,
            "total_count_before": total_urls_before,
            "total_count_after": total_urls_after,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


@app.task()
def maintain_shortcode_pool():
    ShortCodeService().refill_pool()


@app.task()
def process_analytics_buffer():
    """Process buffered analytics visits from Redis and bulk insert into database."""
    try:
        redis_conn = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
        )
        visits_to_process = []
        for _ in range(100):
            visit_json = redis_conn.lpop("analytics:visits")
            if not visit_json:
                break
            visit_data = json.loads(visit_json.decode("utf-8"))
            visit_data["timestamp"] = datetime.fromisoformat(visit_data["timestamp"])
            visits_to_process.append(
                Visit(
                    url_id=visit_data["url_id"],
                    hashed_ip=visit_data["hashed_ip"],
                    geolocation=visit_data["geolocation"],
                    operating_system=visit_data["operating_system"],
                    browser=visit_data["browser"],
                    device=visit_data["device"],
                    referrer=visit_data["referrer"],
                    new_visitor=visit_data["new_visitor"],
                    timestamp=visit_data["timestamp"],
                )
            )
        if visits_to_process:
            Visit.objects.bulk_create(visits_to_process)
        return {
            "status": "success",
            "processed_count": len(visits_to_process),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
