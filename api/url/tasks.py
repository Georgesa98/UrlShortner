import json
import logging
from typing import Dict, Any

from api.analytics.models import Visit
from api.admin_panel.fraud.models import FraudIncident
from config.redis_utils import get_redis_client
from api.url.services.ShortCodeService import ShortCodeService
from config.celery import app
from datetime import datetime
from django.utils import timezone
from api.url.models import Url, UrlStatus
from django.conf import settings
from django.core.management import call_command
from api.url.link_rot.LinkRotService import LinkRotService

logger = logging.getLogger(__name__)


@app.task()
def deactivate_expired_urls_task() -> None:
    try:
        total_expired_urls_before = Url.objects.filter(
            expiry_date__lte=timezone.now()
        ).count()
        total_urls_before = (
            Url.objects.select_related("url_status")
            .filter(url_status__state=UrlStatus.State.ACTIVE)
            .count()
        )
        call_command("deactivate_expired_urls", delete=False)
        total_urls_after = (
            Url.objects.select_related("url_status")
            .filter(url_status__state=UrlStatus.State.ACTIVE)
            .count()
        )
        cleaned_count = total_urls_before - total_urls_after
        return {
            "status": "success",
            "cleaned_count": cleaned_count,
            "expired_count_before": total_expired_urls_before,
            "total_count_before": total_urls_before,
            "total_count_after": total_urls_after,
            "timestamp": timezone.now().isoformat(),
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": timezone.now().isoformat(),
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
                    new_visitor=visit_data["new_visitor"],
                    referer=visit_data["referer"],
                    timestamp=visit_data["timestamp"],
                )
            )

        for _ in range(50):
            fraud_json = redis_conn.lpop("analytics:fraud")
            if not fraud_json:
                break
            fraud_data = json.loads(fraud_json)

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
            "timestamp": timezone.now().isoformat(),
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": timezone.now().isoformat(),
        }


@app.task()
def populate_link_rot_queue(
    days_threshold: int = 7, batch_size: int = 1000
) -> Dict[str, Any]:
    """
    Periodic task to fetch URLs needing health check and store them in Redis queue.

    Args:
        days_threshold: Number of days since last check to consider for re-checking
        batch_size: Maximum number of URLs to fetch and add to the queue

    Returns:
        Dictionary with status information
    """
    try:
        redis_conn = get_redis_client()
        service = LinkRotService(batch_size=batch_size)
        url_ids = service.get_urls_needing_check(days_threshold)

        if not url_ids:
            logger.info("No URLs found that need link rot checking")
            return {
                "status": "success",
                "message": "No URLs found that need link rot checking",
                "urls_added": 0,
                "timestamp": timezone.now().isoformat(),
            }

        for url_id in url_ids:
            redis_conn.rpush("link_rot:urls_to_check", str(url_id))

        logger.info(f"Added {len(url_ids)} URLs to link rot queue in Redis")

        if url_ids:
            check_and_update_link_rot_batch.delay()

        return {
            "status": "success",
            "urls_added": len(url_ids),
            "url_ids": url_ids,
            "timestamp": timezone.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error in populate_link_rot_queue: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": timezone.now().isoformat(),
        }


@app.task()
def check_and_update_link_rot_batch(batch_size: int = 10) -> Dict[str, Any]:
    """
    Task to check and update a small batch of URLs from the Redis queue.
    If there are more URLs in the queue after processing, it schedules itself again.

    Args:
        batch_size: Number of URLs to process in this batch

    Returns:
        Dictionary with status information
    """
    try:
        redis_conn = get_redis_client()
        service = LinkRotService(batch_size=batch_size)

        url_ids_batch = []

        for _ in range(batch_size):
            url_id = redis_conn.lpop("link_rot:urls_to_check")
            if url_id is None:
                break
            url_ids_batch.append(int(url_id))

        if not url_ids_batch:
            logger.info("Link rot queue is empty, nothing to process")
            service.close()
            return {
                "status": "success",
                "total_processed": 0,
                "message": "No URLs to process in link rot queue",
                "timestamp": timezone.now().isoformat(),
            }

        logger.info(f"Processing batch of {len(url_ids_batch)} URLs for link rot check")

        health_results = service.check_batch_health(url_ids_batch)

        status_updates = []
        for result in health_results:
            status_updates.append(
                {
                    "url_id": result["url_id"],
                    "status": result["status"],
                    "reason": result["error"],
                }
            )

        update_results = service.bulk_update_statuses(status_updates)

        processed_count = len(health_results)

        logger.info(
            f"Completed batch: {len(health_results)} URLs processed, "
            f"{update_results['success']} updated successfully"
        )

        remaining_count = redis_conn.llen("link_rot:urls_to_check")
        if remaining_count > 0:
            logger.info(
                f"{remaining_count} URLs remaining in link rot queue, scheduling next batch"
            )
            check_and_update_link_rot_batch.apply_async(
                kwargs={"batch_size": batch_size},
                countdown=2,
            )

        service.close()

        return {
            "status": "success",
            "total_processed": processed_count,
            "message": f"Processed {processed_count} URLs for link rot checking, {remaining_count} remaining",
            "timestamp": timezone.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error in check_and_update_link_rot_batch: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": timezone.now().isoformat(),
        }
