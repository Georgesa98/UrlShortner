from config.settings_utils import get_throttle_rates
from config.redis_utils import get_redis_client
import time
from rest_framework.throttling import SimpleRateThrottle
from api.admin_panel.fraud.FraudService import FraudService


class RedisRateLimiter:
    def __init__(self):
        self.redis_client = get_redis_client()

    def is_allowed(self, key: str, limit: int, window: int) -> tuple[bool, dict]:
        now = time.time()
        window_key = f"rate_limit:{key}"

        pipe = self.redis_client.pipeline()
        pipe.zremrangebyscore(window_key, "-inf", now - window)
        pipe.zcard(window_key)
        results = pipe.execute()

        current_count = results[1]

        is_allowed = current_count < limit

        if is_allowed:
            pipe = self.redis_client.pipeline()
            pipe.zadd(window_key, {f"{now}": now})
            pipe.expire(window_key, window)
            pipe.execute()

        remaining = max(0, limit - current_count - (1 if is_allowed else 0))
        reset_time = int(now + window)
        metadata = {
            "remaining": remaining,
            "reset": reset_time,
            "limit": limit,
        }

        return is_allowed, metadata


class BaseRedisThrottle(SimpleRateThrottle):
    redis_limiter = RedisRateLimiter()

    def allow_request(self, request, view):
        if self.rate is None:
            return True

        key = self.get_cache_key(request, view)

        if key is None:
            return True

        self.key = key
        self.num_requests, self.duration = self.parse_rate(self.rate)
        is_allowed, metadata = self.redis_limiter.is_allowed(
            key, self.num_requests, self.duration
        )

        self.metadata = metadata

        request.throttle_metadata = metadata

        if not is_allowed:
            FraudService.flag_throttle_violation(request, view, self.rate)

        return is_allowed

    def wait(self):
        if hasattr(self, "metadata"):
            return max(0, self.metadata["reset"] - time.time())
        return None


class IPRateThrottle(BaseRedisThrottle):
    scope = "ip"

    def get_rate(self):
        return get_throttle_rates()["ip"]

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            return None
        ip = self.get_ident(request)
        return f"throttle_ip:{ip}"


class UserRateThrottle(BaseRedisThrottle):
    scope = "user"

    def get_rate(self):
        return get_throttle_rates()["user"]

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            return f"throttle_user:{request.user.pk}"
        return None
