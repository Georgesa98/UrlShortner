import json

from api.analytics.models import Visit
from config.redis_utils import get_redis_client
from api.url.services.ShortCodeService import ShortCodeService
from config.celery import app
from datetime import datetime, timezone
from api.url.models import Url
from api.admin_panel.fraud.models import FraudIncident
from django.conf import settings
from django.core.management import call_command


@app.task()
def deactivate_expired_urls_task() -> None:
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
def maintain_shortcode_pool() -> None:
    ShortCodeService().refill_pool()


@app.task()
def process_analytics_buffer() -> None:
    """Process buffered analytics data from Redis: visits, counters, and fraud incidents."""
    try:
        redis_conn = get_redis_client()
        visits_to_process = []
        fraud_incidents = []
        url_updates = {}

        for _ in range(100):
            visit_json = redis_conn.lpop("analytics:visits")
            if not visit_json:
                break
            visit_data = json.loads(visit_json)
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
                    timestamp=visit_data["timestamp"],
                )
            )

        for _ in range(50):
            fraud_json = redis_conn.lpop("analytics:fraud")
            if not fraud_json:
                break
            fraud_data = json.loads(fraud_json)
            from api.admin_panel.fraud.models import FraudIncident

            fraud_incidents.append(
                FraudIncident(
                    incident_type=fraud_data["incident_type"],
                    details=fraud_data["details"],
                    severity=fraud_data["severity"],
                    url_id=fraud_data["url_id"],
                )
            )

        url_keys = redis_conn.keys("url:*:visits")
        for key in url_keys:
            url_id = key.split(":")[1]
            visits_incr = int(redis_conn.getdel(key) or 0)
            unique_visits_incr = int(
                redis_conn.getdel(f"url:{url_id}:unique_visits") or 0
            )
            last_accessed_str = redis_conn.getdel(f"url:{url_id}:last_accessed")
            if visits_incr or unique_visits_incr or last_accessed_str:
                url_updates[url_id] = {
                    "visits_incr": visits_incr,
                    "unique_visits_incr": unique_visits_incr,
                    "last_accessed": (
                        datetime.fromisoformat(last_accessed_str)
                        if last_accessed_str
                        else None
                    ),
                }

        if visits_to_process:
            Visit.objects.bulk_create(visits_to_process)
        if fraud_incidents:
            FraudIncident.objects.bulk_create(fraud_incidents)
        for url_id, updates in url_updates.items():
            url = Url.objects.get(id=url_id)
            url.visits += updates["visits_incr"]
            url.unique_visits += updates["unique_visits_incr"]
            if updates["last_accessed"]:
                url.last_accessed = updates["last_accessed"]
            url.save()

        return {
            "status": "success",
            "visits_processed": len(visits_to_process),
            "fraud_processed": len(fraud_incidents),
            "urls_updated": len(url_updates),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
