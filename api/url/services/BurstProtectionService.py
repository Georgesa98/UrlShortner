from django.conf import settings
from api.url.models import Url, UrlStatus
from django.utils import timezone
from api.admin_panel.fraud.FraudService import FraudService
from config.redis_utils import get_redis_client


class BurstProtectionService:
    """Service for detecting and preventing burst traffic on URLs."""

    def __init__(self) -> None:
        """Initialize the BurstProtectionService with Redis client."""
        self.redis_client = get_redis_client()
        self.default_thresholds = {
            "short_term_window": 10,  # seconds
            "short_term_limit": 10,
            "medium_term_window": 60,  # seconds
            "medium_term_limit": 50,
            "long_term_window": 3600,  # seconds
            "long_term_limit": 1000,
        }

    def _detect_burst(self, ip: str, short_url: str) -> bool:
        """Detect if current traffic constitutes a burst.

        Args:
            ip (str): The IP address.
            short_url (str): The short URL identifier.

        Returns:
            bool: True if burst detected, False otherwise.
        """
        timestamp = timezone.now().timestamp()
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

    def _check_window_burst(self, key: str, start_time: float, threshold: int) -> bool:
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
            timezone.now().timestamp(),
        )
        return count >= threshold

    def _flag_url(self, short_url, ip) -> None:
        """Flag a URL as having excessive traffic.

        Args:
            short_url (str): The short URL to flag.
            ip (str): The IP address triggering the flag.
        """
        url_instance = Url.objects.select_related("url_status").get(short_url=short_url)
        if url_instance.url_status.state != UrlStatus.State.FLAGGED:
            url_instance.url_status.state = UrlStatus.State.FLAGGED
            url_instance.url_status.reason = "Too many requests on the url"
            url_instance.url_status.save()
            FraudService.flag_burst_protection(url_instance, ip)

    def _track_click(self, short_url: str, ip: str) -> None:
        """Track a click for burst protection.

        Args:
            short_url (str): The short URL identifier.
            ip (str): The IP address.
        """
        timestamp = timezone.now().timestamp()
        url_key = f"burst_protection:url:{short_url}"
        ip_key = f"burst_protection:ip:{ip}"

        # Add new entry
        self.redis_client.zadd(url_key, {str(timestamp): timestamp})
        self.redis_client.zadd(ip_key, {str(timestamp): timestamp})

        # Clean up old entries beyond long_term_window
        cutoff_time = timestamp - self.default_thresholds["long_term_window"]
        self.redis_client.zremrangebyscore(url_key, "-inf", cutoff_time)
        self.redis_client.zremrangebyscore(ip_key, "-inf", cutoff_time)

    def check_burst(self, ip: str, short_url: str) -> bool:
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
                    self._flag_url(short_url, ip)
                    return False
                self._track_click(short_url, ip)
                return True
            finally:
                lock.release()
        except Exception as e:
            return False
