from datetime import timedelta
import logging
from typing import List, Dict, Any, Optional

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3.exceptions import MaxRetryError, ConnectTimeoutError

from api.url.models import Url, UrlStatus


logger = logging.getLogger(__name__)


class LinkRotService:
    def __init__(self, batch_size: int = 100, timeout: int = 10):
        self.batch_size = batch_size
        self.timeout = timeout
        self.session: Session = self._create_session()

    def close(self):
        """Close the HTTP session to free resources"""
        if self.session:
            self.session.close()

    def _create_session(self) -> Session:
        """Create a session with retry strategy and proper configuration"""
        session = Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update({"User-Agent": "UrlShortener Link Rot Checker 1.0"})
        return session

    def check_url_health(self, url_instance: Url) -> Dict[str, Any]:
        """
        Check the health of a single URL and return status information

        Args:
            url_instance: The URL instance to check

        Returns:
            Dictionary containing status information
        """
        try:
            try:
                response = self.session.head(
                    url_instance.long_url, timeout=self.timeout, allow_redirects=True
                )
            except Exception:
                response = self.session.get(
                    url_instance.long_url, timeout=self.timeout, allow_redirects=True
                )

            if 200 <= response.status_code < 400:
                status = UrlStatus.State.ACTIVE
                error = None
            else:
                status = UrlStatus.State.BROKEN
                error = f"HTTP {response.status_code}"

        except ConnectTimeoutError as e:
            logger.warning(f"Connection timeout for {url_instance.long_url}: {str(e)}")
            status = UrlStatus.State.BROKEN
            error = f"Connection timeout: {str(e)}"
        except MaxRetryError as e:
            logger.warning(f"Max retry error for {url_instance.long_url}: {str(e)}")
            status = UrlStatus.State.BROKEN
            error = f"Max retry error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error checking {url_instance.long_url}: {str(e)}")
            status = UrlStatus.State.BROKEN
            error = f"Unexpected error: {str(e)}"

        return {
            "status": status,
            "url_id": url_instance.id,
            "destination": url_instance.long_url,
            "error": error,
        }

    def check_batch_health(self, url_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Check health of a batch of URLs

        Args:
            url_ids: List of URL IDs to check

        Returns:
            List of status dictionaries for each URL
        """
        results = []
        try:
            urls = Url.objects.filter(id__in=url_ids).select_related("url_status")

            for url in urls:
                result = self.check_url_health(url)
                results.append(result)

        except Exception as e:
            logger.error(f"Error in batch health check: {str(e)}")
            return []

        return results

    def update_url_status(
        self, url_id: int, new_status: str, reason: Optional[str] = None
    ) -> bool:
        """
        Update the status of a specific URL in the database

        Args:
            url_id: ID of the URL to update
            new_status: New status to set
            reason: Optional reason for the status change

        Returns:
            True if update was successful, False otherwise
        """
        try:
            with transaction.atomic():
                url = (
                    Url.objects.select_for_update()
                    .select_related("url_status")
                    .get(id=url_id)
                )
                url_status = url.url_status
                if not url_status:
                    url_status = UrlStatus.objects.create(url=url)

                url_status.state = new_status
                url_status.reason = reason
                url_status.last_checked = timezone.now()
                url_status.save()

                logger.info(f"Updated status for URL {url_id} to {new_status}")
                return True

        except Url.DoesNotExist:
            logger.error(f"URL with ID {url_id} does not exist")
            return False
        except Exception as e:
            logger.error(f"Error updating status for URL {url_id}: {str(e)}")
            return False

    def bulk_update_statuses(
        self, status_updates: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        Bulk update URL statuses from a list of status updates

        Args:
            status_updates: List of dictionaries with 'url_id', 'status', and optional 'reason'

        Returns:
            Dictionary with counts of successful and failed updates
        """
        success_count = 0
        failure_count = 0

        try:
            with transaction.atomic():
                url_ids = [update["url_id"] for update in status_updates]

                urls_with_statuses = Url.objects.filter(id__in=url_ids).select_related(
                    "url_status"
                )

                url_status_map = {}
                for url in urls_with_statuses:
                    if hasattr(url, "url_status") and url.url_status:
                        url_status_map[url.id] = url.url_status
                    else:
                        new_status = UrlStatus.objects.create(url=url)
                        url_status_map[url.id] = new_status

                url_statuses_to_update = []
                processed_url_ids = set()

                for update in status_updates:
                    url_id = update["url_id"]
                    if url_id in url_status_map:
                        url_status = url_status_map[url_id]
                        url_status.state = update["status"]
                        url_status.reason = update.get("reason")
                        url_status.last_checked = timezone.now()
                        url_statuses_to_update.append(url_status)
                        processed_url_ids.add(url_id)
                    else:
                        logger.error(
                            f"URL with ID {update['url_id']} does not exist or has no status"
                        )
                        failure_count += 1

                unprocessed_count = len(url_ids) - len(processed_url_ids)
                failure_count += unprocessed_count

                if url_statuses_to_update:
                    UrlStatus.objects.bulk_update(
                        url_statuses_to_update, ["state", "reason"], batch_size=100
                    )
                    success_count = len(url_statuses_to_update)

        except Exception as e:
            logger.error(f"Error in bulk update: {str(e)}")
            return {
                "success": success_count,
                "failure": failure_count + len(status_updates) - success_count,
            }

        return {"success": success_count, "failure": failure_count}

    def get_urls_needing_check(self, days_threshold: int = 7) -> List[int]:
        """
        Get IDs of URLs that need health checking based on criteria

        Args:
            days_threshold: Number of days since last check to consider for re-checking

        Returns:
            List of URL IDs that need checking
        """
        try:
            threshold_date = timezone.now() - timedelta(days=days_threshold)
            urls_to_check = (
                Url.objects.filter(created_at__gte=threshold_date)
                .exclude(url_status__state=UrlStatus.State.BROKEN)
                .filter(
                    Q(url_status__isnull=True)
                    | Q(url_status__last_checked__lt=threshold_date)
                )
                .values_list("id", flat=True)[: self.batch_size]
            )

            return list(urls_to_check)

        except Exception as e:
            logger.error(f"Error getting URLs for checking: {str(e)}")
            return []
