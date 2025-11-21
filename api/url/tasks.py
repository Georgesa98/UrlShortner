from config.celery import app
from datetime import datetime, timezone
from api.url.models import Url
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
