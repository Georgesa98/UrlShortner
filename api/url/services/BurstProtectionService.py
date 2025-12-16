import redis
from django.conf import settings
from api.url.models import Url, UrlStatus
from datetime import datetime, timezone


class BurstProtectionService:
    """Service for detecting and preventing burst traffic on URLs."""

    def __init__(self):
        """Initialize the BurstProtectionService with Redis client."""
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
        )

    def _detect_burst(self, ip: str, short_url: str):
        """Detect if current traffic constitutes a burst.

        Args:
            ip (str): The IP address.
            short_url (str): The short URL identifier.

        Returns:
            bool: True if burst detected, False otherwise.
        """
        timestamp = datetime.now(timezone.utc).timestamp()
        url_key = f"burst_protection:url:{short_url}"
        ip_key = f"burst_protection:ip:{ip}"
        windows = [
            ("short_term_window", "short_term_limit"),
            ("medium_term_window", "medium_term_limit"),
            ("long_term_window", "long_term_limit"),
        ]

        for window_key, limit_key in windows:
            window = self.default_thresholds[window_key]
            limit = self.default_thresholds[limit_key]

            if self._check_window_burst(ip_key, timestamp - window, limit):
                return True
            if self._check_window_burst(url_key, timestamp - window, limit):
                return True
        return False

    def _check_window_burst(self, key: str, start_time: float, threshold: int):
        """Check if request count exceeds threshold in a time window.

        Args:
            key (str): Redis key for tracking.
            start_time (float): Start timestamp of the window.
            threshold (int): Maximum allowed requests.

        Returns:
            bool: True if threshold exceeded.
        """
        count = self.redis_client.zcount(
            key,
            start_time,
            datetime.now(timezone.utc).timestamp(),
        )
        return count >= threshold

    def _flag_url(self, short_url):
        """Flag a URL as having excessive traffic.

        Args:
            short_url (str): The short URL to flag.
        """
        url_instance = Url.objects.get(short_url=short_url)
        url_status_instance = UrlStatus.objects.get(url=url_instance)
        if url_status_instance.state != UrlStatus.State.FLAGGED:
            url_status_instance.state = UrlStatus.State.FLAGGED
            url_status_instance.reason = "Too many requests on the url"
            url_status_instance.save()

    def check_burst(self, ip: str, short_url: str):
        """Check and handle burst protection for a request.

        Args:
            ip (str): The IP address.
            short_url (str): The short URL identifier.

        Returns:
            bool: True if request allowed, False if blocked.
        """
        from redis.lock import Lock

        lock_key = f"burst_protection:lock:{short_url}:{ip}"
        lock = Lock(self.redis_client, lock_key, timeout=3, blocking_timeout=1)
        try:
            acquired = lock.acquire(blocking=True)
            if not acquired:
                return False
            try:
                if self._detect_burst(ip, short_url):
                    self._flag_url(short_url)
                    return False
                self._track_click(short_url, ip)
                return True
            finally:
                lock.release()
        except Exception as e:
            return False


_burst_protection_instance = None


def get_burst_protection_service():
    """Get singleton instance of BurstProtectionService.

    Returns:
        BurstProtectionService: The singleton instance.
    """
    global _burst_protection_instance
    if _burst_protection_instance is None:
        _burst_protection_instance = BurstProtectionService()
    return _burst_protection_instance
