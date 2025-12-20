import pytest
from api.analytics.utils import convert_ip_to_location
from config.redis_utils import get_redis_client


@pytest.fixture(scope="function")
def redis_client():
    client = get_redis_client()
    yield client


def test_cache_miss_valid_ipv4(redis_client):
    """Test cache miss with valid IPv4 address"""
    ip = "8.8.8.8"
    result = convert_ip_to_location(ip)
    assert isinstance(result, str)
    key = f"ip_country:{ip}"
    cached = redis_client.get(key)
    assert cached is not None
    ttl = redis_client.ttl(key)
    assert ttl == 86400
    assert result == cached


def test_cache_hit(redis_client):
    """Test cache hit for existing IP address"""
    ip = "8.8.4.4"
    key = f"ip_country:{ip}"
    expected_country = "United States"
    redis_client.setex(key, 86400, expected_country)
    result = convert_ip_to_location(ip)
    assert result == expected_country
    ttl = redis_client.ttl(key)
    assert ttl > 0


def test_cache_miss_unknown_ip(redis_client):
    """Test cache miss with unknown IP address"""
    ip = "192.168.1.1"
    result = convert_ip_to_location(ip)
    assert result == "Unknown"
    key = f"ip_country:{ip}"
    cached = redis_client.get(key)
    assert cached == (b"" if isinstance(cached, bytes) else "")
    ttl = redis_client.ttl(key)
    assert ttl == 86400


def test_invalid_ip(redis_client):
    """Test handling of invalid IP address"""
    ip = "invalid.ip.address"
    result = convert_ip_to_location(ip)
    assert result == "Unknown"
    key = f"ip_country:{ip}"
    cached = redis_client.get(key)
    assert cached == (b"" if isinstance(cached, bytes) else "")
    ttl = redis_client.ttl(key)
    assert ttl == 86400


def test_ipv6_address(redis_client):
    """Test handling of IPv6 address"""
    ip = "2001:4860:4860::8888"
    result = convert_ip_to_location(ip)
    assert isinstance(result, str)
    key = f"ip_country:{ip}"
    cached = redis_client.get(key)
    assert cached is not None
    ttl = redis_client.ttl(key)
    assert ttl == 86400


def test_geocoder_exception_handling(redis_client):
    """Test exception handling in geocoder"""
    ip = "255.255.255.255"
    result = convert_ip_to_location(ip)
    assert result == "Unknown"
    key = f"ip_country:{ip}"
    cached = redis_client.get(key)
    assert cached == (b"" if isinstance(cached, bytes) else "")
    ttl = redis_client.ttl(key)
    assert ttl == 86400
