import pytest

from api.throttling import RedisRateLimiter
from unittest.mock import patch

from api.url.services.ShortCodeService import ShortCodeService


@pytest.fixture(autouse=True)
def clear_redis():
    limiter = RedisRateLimiter()
    limiter.redis_client.flushdb()
    ShortCodeService().refill_pool(50)
    yield
    limiter.redis_client.flushdb()


@pytest.fixture
def disable_burst_protection():
    with patch(
        "api.url.services.BurstProtectionService.BurstProtectionService.check_burst",
        return_value=True,
    ):
        yield
