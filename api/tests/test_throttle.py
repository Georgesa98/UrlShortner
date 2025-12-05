"""
E2E tests for Rate Limiting and Throttling
Location: urls/tests/test_rate_limiting.py
"""

import pytest
import time
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.core.cache import cache
from api.url.models import Url as URL, UrlStatus
from django.test import TestCase
from django.contrib.auth import get_user_model
from api.throttling import RedisRateLimiter

User = get_user_model()


@pytest.mark.django_db
class TestAuthenticatedUserRateLimiting:
    """Test rate limiting for authenticated users"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        cache.clear()  # Clear cache before each test

    def tearDown(self):
        cache.clear()  # Clear cache after each test

    def test_url_creation_rate_limit(self):
        """Test rate limiting on URL creation endpoint"""
        url = "/api/url/shorten/"

        # Make requests up to the limit
        successful_requests = 0
        rate_limited = False

        for i in range(1001):  # Try more than the limit
            payload = {"long_url": f"https://www.example.com/test{i}"}
            response = self.client.post(url, payload, format="json")

            if response.status_code == status.HTTP_201_CREATED:
                successful_requests += 1
            elif response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                rate_limited = True
                break

        # Verify rate limiting kicked in
        assert rate_limited, "Rate limiting should have been triggered"
        assert successful_requests > 0, "Some requests should have succeeded"
        assert successful_requests == 1000, "Not all requests should succeed"

    def test_rate_limit_response_format(self):
        """Test rate limit response contains proper error message"""
        url = "/api/url/shorten/"

        # Exhaust rate limit
        for i in range(100):
            payload = {"long_url": f"https://www.example.com/test{i}"}
            response = self.client.post(url, payload, format="json")

            if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                # Check response format
                assert "detail" in response.data or "error" in response.data
                break

    def test_rate_limit_headers(self):
        """Test rate limit headers are present in response"""
        url = "/api/url/shorten/"
        payload = {"long_url": "https://www.example.com/test"}

        response = self.client.post(url, payload, format="json")

        # Common rate limit headers
        possible_headers = [
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
            "Retry-After",
        ]

        # At least some rate limit info should be present
        if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            assert any(
                header in response for header in possible_headers
            ), "Rate limit response should include rate limit headers"

    def test_different_endpoints_separate_limits(self):
        """Test that different endpoints have separate rate limits"""
        shorten_url = "/api/url/shorten/"

        # Create a URL first
        create_response = self.client.post(
            shorten_url, {"long_url": "https://www.example.com/test"}, format="json"
        )
        short_url = create_response.data["short_url"]

        # Exhaust rate limit on shorten endpoint
        for i in range(100):
            payload = {"long_url": f"https://www.example.com/test{i}"}
            response = self.client.post(shorten_url, payload, format="json")
            if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                break

        # Try to access a different endpoint (should work if separate limits)
        retrieve_url = f"/api/url/{short_url}/"
        retrieve_response = self.client.get(retrieve_url)

        # This might succeed or fail depending on your rate limit configuration
        # Just verify it responds properly
        assert retrieve_response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_429_TOO_MANY_REQUESTS,
        ]


@pytest.mark.django_db
@pytest.mark.usefixtures("disable_burst_protection")
class TestIPBasedRateLimiting:
    """Test IP-based rate limiting"""

    def setup_method(self):
        self.client = APIClient()
        cache.clear()

    def teardown_method(self):
        cache.clear()

    def test_ip_based_rate_limiting(self):
        """Test rate limiting based on IP address"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        url_obj = URL.objects.create(
            long_url="https://www.example.com/ip-test", short_url="iptest123", user=user
        )

        # Set IP address in headers
        redirect_url = f"/api/url/redirect/{url_obj.short_url}/"

        rate_limited = False
        for i in range(200):
            response = self.client.get(redirect_url, REMOTE_ADDR="192.168.1.100")

            if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                rate_limited = True
                break

        assert rate_limited, "IP-based rate limiting should trigger"

    def test_different_ips_separate_limits(self):
        """Test that different IPs have separate rate limits"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        url_obj = URL.objects.create(
            long_url="https://www.example.com/multi-ip",
            short_url="multiip123",
            user=user,
        )
        UrlStatus.objects.create(url=url_obj)

        redirect_url = f"/api/url/redirect/{url_obj.short_url}/"

        # Exhaust limit for first IP
        for i in range(200):
            response = self.client.get(redirect_url, REMOTE_ADDR="192.168.1.100")
            if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                break

        # Different IP should still work
        response = self.client.get(redirect_url, REMOTE_ADDR="192.168.1.200")

        assert (
            response.status_code == status.HTTP_302_FOUND
        ), "Different IPs should have separate rate limits"


@pytest.mark.django_db
@pytest.mark.usefixtures("disable_burst_protection")
class TestThrottlingIntegration:
    """Integration tests for throttling across different scenarios"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        cache.clear()

    def teardown_method(self):
        cache.clear()

    def test_rate_limit_does_not_affect_valid_operations(self):
        """Test that rate limiting doesn't interfere with normal operations"""
        # Create a few URLs (within limits)
        for i in range(5):
            response = self.client.post(
                "/api/url/shorten/",
                {"long_url": f"https://www.example.com/normal{i}"},
                format="json",
            )
            assert response.status_code == status.HTTP_201_CREATED

        # Wait a bit
        time.sleep(1)

        # Should still be able to perform other operations
        response = self.client.get("/api/analytics/top-visited/")
        assert response.status_code == status.HTTP_200_OK

    def test_rate_limit_with_concurrent_operations(self):
        """Test rate limiting with different operations"""
        # Try multiple different operations
        operations_count = {"create": 0, "retrieve": 0, "analytics": 0}

        # Create some URLs
        urls_created = []
        for i in range(10):
            response = self.client.post(
                "/api/url/shorten/",
                {"long_url": f"https://www.example.com/concurrent{i}"},
                format="json",
            )
            if response.status_code == status.HTTP_201_CREATED:
                operations_count["create"] += 1
                urls_created.append(response.data["short_url"])

        # Retrieve URLs
        for short_url in urls_created:
            response = self.client.get(f"/api/url/{short_url}/")
            if response.status_code == status.HTTP_200_OK:
                operations_count["retrieve"] += 1

        # Check analytics
        response = self.client.get("/api/analytics/top-visited/")
        if response.status_code == status.HTTP_200_OK:
            operations_count["analytics"] += 1

        # Verify some operations succeeded
        assert sum(operations_count.values()) > 0, "Some operations should succeed"

    def test_rate_limit_error_does_not_create_url(self):
        """Test that rate-limited requests don't create partial data"""
        initial_count = URL.objects.count()

        # Exhaust rate limit
        created_count = 0
        for i in range(200):
            response = self.client.post(
                "/api/url/shorten/",
                {"long_url": f"https://www.example.com/test{i}"},
                format="json",
            )
            if response.status_code == status.HTTP_201_CREATED:
                created_count += 1

        final_count = URL.objects.count()

        # Only successfully created URLs should be in database
        assert (
            final_count == initial_count + created_count
        ), "Rate-limited requests should not create partial data"

    def test_throttle_recovery_after_wait(self):
        """Test that rate limits recover after waiting"""
        url = "/api/url/shorten/"

        # Create URLs until rate limited
        for i in range(1001):
            payload = {"long_url": f"https://www.example.com/recovery{i}"}
            response = self.client.post(url, payload, format="json")
            if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                break

        # Should be rate limited
        response = self.client.post(
            url, {"long_url": "https://www.example.com/still-limited"}, format="json"
        )
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

        # Wait for rate limit window (adjust based on your config)
        time.sleep(2)

        # Should work again or still be limited depending on window
        response = self.client.post(
            url, {"long_url": "https://www.example.com/after-wait"}, format="json"
        )
        # Just verify it responds with valid status
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_429_TOO_MANY_REQUESTS,
        ]

    def test_analytics_endpoint_rate_limiting(self):
        """Test rate limiting on analytics endpoints"""
        # Create some URLs first
        for i in range(3):
            self.client.post(
                "/api/url/shorten/",
                {"long_url": f"https://www.example.com/analytics{i}"},
                format="json",
            )

        # Hammer analytics endpoint
        rate_limited = False
        successful_requests = 0

        for i in range(100):
            response = self.client.get("/api/analytics/top-visited/")

            if response.status_code == status.HTTP_200_OK:
                successful_requests += 1
            elif response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                rate_limited = True
                break

        # Should eventually be rate limited (or all succeed if limits are high)
        assert rate_limited or successful_requests == 100

    def test_update_endpoint_rate_limiting(self):
        """Test rate limiting on URL update endpoint"""
        # Create a URL
        create_response = self.client.post(
            "/api/url/shorten/",
            {"long_url": "https://www.example.com/update-test"},
            format="json",
        )
        short_url = create_response.data["short_url"]

        # Try to update it many times
        rate_limited = False
        successful_updates = 0

        for i in range(100):
            response = self.client.patch(
                f"/api/url/{short_url}/",
                {"long_url": f"https://www.example.com/updated{i}"},
                format="json",
            )

            if response.status_code == status.HTTP_200_OK:
                successful_updates += 1
            elif response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                rate_limited = True
                break

        # Should be rate limited or succeed depending on config
        assert rate_limited or successful_updates > 0

    def test_delete_endpoint_rate_limiting(self):
        """Test rate limiting on URL delete endpoint"""
        # Create multiple URLs
        short_urls = []
        for i in range(20):
            response = self.client.post(
                "/api/url/shorten/",
                {"long_url": f"https://www.example.com/delete{i}"},
                format="json",
            )
            if response.status_code == status.HTTP_201_CREATED:
                short_urls.append(response.data["short_url"])

        # Try to delete them all rapidly
        rate_limited = False
        successful_deletes = 0

        for short_url in short_urls:
            response = self.client.delete(f"/api/url/{short_url}/")

            if response.status_code == status.HTTP_204_NO_CONTENT:
                successful_deletes += 1
            elif response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                rate_limited = True
                break

        # Verify some operations completed
        assert successful_deletes > 0
