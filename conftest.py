import pytest

from api.throttling import RedisRateLimiter
from unittest.mock import patch


@pytest.fixture(autouse=True)
def clear_redis():
    limiter = RedisRateLimiter()
    limiter.redis_client.flushdb()
    yield
    limiter.redis_client.flushdb()


@pytest.fixture
def disable_burst_protection():
    with patch("api.url.service.BurstProtectionService.check_burst", return_value=True):
        yield
