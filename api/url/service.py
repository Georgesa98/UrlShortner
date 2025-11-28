import redis
from django.conf import settings
from api.url.models import Url, UrlStatus
from api.url.utils import generator
from datetime import datetime, timezone
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


class BurstProtectionService:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
        )

        self.default_thresholds = {
            "short_term_window": 10,
            "short_term_limit": 10,
            "medium_term_window": 60,
            "medium_term_limit": 50,
            "long_term_window": 3600,
            "long_term_limit": 1000,
        }

    def _track_click(self, short_url: str, ip: str):
        timestamp = datetime.now(timezone.utc).timestamp()

        url_key = f"burst_protection:url:{short_url}"
        ip_key = f"burst_protection:ip:{ip}"

        self.redis_client.zadd(url_key, {f"request_{timestamp}": timestamp})
        self.redis_client.zadd(ip_key, {f"request_{timestamp}": timestamp})

        cutoff_time = timestamp - self.default_thresholds["long_term_window"]

        self.redis_client.zremrangebyscore(url_key, "-inf", cutoff_time)
        self.redis_client.zremrangebyscore(ip_key, "-inf", cutoff_time)

    def _detect_burst(self, ip: str, short_url: str):
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
        count = self.redis_client.zcount(
            key,
            start_time,
            datetime.now(timezone.utc).timestamp(),
        )
        return count >= threshold

    def _flag_url(self, short_url):
        url_instance = Url.objects.get(short_url=short_url)
        url_status_instance = UrlStatus.objects.get(url=url_instance)
        if url_status_instance.state != UrlStatus.State.FLAGGED:
            url_status_instance.state = UrlStatus.State.FLAGGED
            url_status_instance.reason = "Too many requests on the url"
            url_status_instance.save()

    def check_burst(self, ip: str, short_url: str):
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
    global _burst_protection_instance
    if _burst_protection_instance is None:
        _burst_protection_instance = BurstProtectionService()
    return _burst_protection_instance


class UrlService:

    @staticmethod
    def create_url(validated_data: dict):

        short_url = generator()
        url_instance = Url.objects.create(
            user=validated_data["user"],
            long_url=validated_data["long_url"],
            short_url=short_url,
            expiry_date=(
                validated_data["expiry_date"]
                if "expiry_date" in validated_data
                else None
            ),
        ).save()
        UrlStatus.objects.create(url=url_instance).save()
        return url_instance

    def batch_shorten(validated_data: list, user_id: str):
        urls = []
        for url in validated_data:
            short_url = generator()
            try:
                url_instance = Url.objects.create(
                    user=user_id,
                    long_url=url["long_url"],
                    short_url=short_url,
                    expiry_date=(url["expiry_date"] if "expiry_date" in url else None),
                ).save()
                UrlStatus.objects.create(url=url_instance).save()
                urls.append(url_instance)
            except Exception as e:
                urls.append(str(e))
        return urls

    @staticmethod
    def update_url(instance, validated_data):
        instance.long_url = validated_data.get(
            "long_url", validated_data.get("long_url", instance.long_url)
        )

        instance.expiry_date = validated_data.get(
            "expiry_date", validated_data.get("expiry_date", instance.expiry_date)
        )
        instance.is_active = validated_data.get("is_active", instance.is_active)
        instance.updated_at = datetime.now(timezone.utc)
        instance.save()
        return instance

    @staticmethod
    def fetch_urls_with_filter_and_pagination(
        limit: int, page: int, status: UrlStatus.State, user_id: str
    ):
        queryset = Url.objects.select_related("url_status").filter(user=user_id)
        if status:
            queryset = queryset.filter(url_status__state=status)
        queryset = queryset.order_by("-created_at")
        paginator = Paginator(queryset, limit)
        try:
            paginated_urls = paginator.page(page)
        except PageNotAnInteger:
            paginated_urls = paginator.page(1)
        except EmptyPage:
            paginated_urls = paginated_urls(paginator.num_pages)

        return paginated_urls
