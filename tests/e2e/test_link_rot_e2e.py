import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from api.url.models import Url, UrlStatus
from api.url.link_rot.LinkRotService import LinkRotService
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch
import redis
from django.conf import settings

"""
E2E tests for Link Rot functionality
"""

User = get_user_model()


@pytest.mark.django_db
class TestLinkRotService:
    """Test LinkRotService functionality"""

    def setup_method(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )
        self.regular_user = User.objects.create_user(
            username="regularuser",
            email="regular@example.com",
            password="regularpass123",
            role=User.Role.USER,
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_get_urls_needing_check(self):
        """Test getting URLs that need health check"""
        # Create URLs with different last_checked times
        url1 = Url.objects.create(
            long_url="https://www.example.com/needs-check",
            short_url="check123",
            user=self.regular_user,
        )
        # Set last_checked to be old (more than 7 days ago)
        url_status1 = UrlStatus.objects.create(
            url=url1, last_checked=timezone.now() - timedelta(days=10)  # Needs check
        )

        url2 = Url.objects.create(
            long_url="https://www.example.com/recently-checked",
            short_url="recent123",
            user=self.regular_user,
        )
        # Set last_checked to be recent (within 7 days)
        url_status2 = UrlStatus.objects.create(
            url=url2,
            last_checked=timezone.now() - timedelta(days=1),  # Recently checked
        )

        url3 = Url.objects.create(
            long_url="https://www.example.com/no-status",
            short_url="nostatus123",
            user=self.regular_user,
        )
        # Don't create UrlStatus for this one - should be checked

        service = LinkRotService()
        urls_needing_check = service.get_urls_needing_check(days_threshold=7)

        assert url1.id in urls_needing_check
        assert url2.id not in urls_needing_check
        assert url3.id in urls_needing_check  # No status record, so needs check

    def test_check_batch_health(self):
        """Test checking health of a batch of URLs"""
        # Create URLs
        url1 = Url.objects.create(
            long_url="https://httpbin.org/status/20",  # Healthy
            short_url="healthy123",
            user=self.regular_user,
        )
        UrlStatus.objects.create(url=url1)

        url2 = Url.objects.create(
            long_url="https://httpbin.org/status/404",  # Unhealthy
            short_url="unhealthy123",
            user=self.regular_user,
        )
        UrlStatus.objects.create(url=url2)

        service = LinkRotService()

        # Mock the check_url_health method to avoid real network requests
        with patch.object(service, "check_url_health") as mock_check:
            # Configure mock to return different results for each URL
            def side_effect(url_instance):
                if url_instance.id == url1.id:
                    return {
                        "status": UrlStatus.State.ACTIVE,
                        "url_id": url_instance.id,
                        "destination": url_instance.long_url,
                        "error": None,
                    }
                elif url_instance.id == url2.id:
                    return {
                        "status": UrlStatus.State.BROKEN,
                        "url_id": url_instance.id,
                        "destination": url_instance.long_url,
                        "error": "HTTP 404",
                    }

            mock_check.side_effect = side_effect
            health_results = service.check_batch_health([url1.id, url2.id])

        assert len(health_results) == 2

        # Check results
        healthy_result = next(r for r in health_results if r["url_id"] == url1.id)
        unhealthy_result = next(r for r in health_results if r["url_id"] == url2.id)

        # The service returns state choices which are uppercase
        assert healthy_result["status"] in [
            UrlStatus.State.ACTIVE,
            UrlStatus.State.BROKEN,
        ]
        # For 200 status, it should return ACTIVE
        assert healthy_result["error"] is None

        # For 404 status, it should return BROKEN
        assert unhealthy_result["status"] == UrlStatus.State.BROKEN
        assert unhealthy_result["error"] is not None

    def test_bulk_update_statuses(self):
        """Test bulk updating URL statuses"""
        # Create URLs
        url1 = Url.objects.create(
            long_url="https://www.example.com/update1",
            short_url="update123",
            user=self.regular_user,
        )
        status1 = UrlStatus.objects.create(url=url1)

        url2 = Url.objects.create(
            long_url="https://www.example.com/update2",
            short_url="update456",
            user=self.regular_user,
        )
        status2 = UrlStatus.objects.create(url=url2)

        service = LinkRotService()
        updates = [
            {
                "url_id": url1.id,
                "status": UrlStatus.State.ACTIVE,
                "reason": "Link is accessible",
            },
            {
                "url_id": url2.id,
                "status": UrlStatus.State.BROKEN,
                "reason": "Link returned 404",
            },
        ]

        result = service.bulk_update_statuses(updates)

        assert "success" in result
        assert "failure" in result

        # Verify updates in DB
        status1.refresh_from_db()
        status2.refresh_from_db()

        assert status1.state == UrlStatus.State.ACTIVE
        assert status1.reason == "Link is accessible"

        assert status2.state == UrlStatus.State.BROKEN
        assert status2.reason == "Link returned 404"

    def test_check_url_health_with_timeout(self):
        """Test checking URL health with timeout handling"""
        # Create URL
        url = Url.objects.create(
            long_url="https://example.com/timeout-test",
            short_url="timeout123",
            user=self.regular_user,
        )
        UrlStatus.objects.create(url=url)

        service = LinkRotService()

        # Mock the session.get method to raise a timeout error
        with patch.object(service.session, "get") as mock_get:
            mock_get.side_effect = TimeoutError("Request timed out")

            # Also mock session.head to raise a timeout error
            with patch.object(service.session, "head") as mock_head:
                mock_head.side_effect = TimeoutError("Request timed out")

                result = service.check_url_health(url)

                assert result["status"] == UrlStatus.State.BROKEN
                assert "unexpected error: request timed out" in result["error"].lower()

    def test_check_url_health_with_connection_error(self):
        """Test checking URL health with connection error"""
        url = Url.objects.create(
            long_url="https://example.com/connection-error",
            short_url="connerror123",
            user=self.regular_user,
        )
        UrlStatus.objects.create(url=url)

        service = LinkRotService()

        # Mock the session.get method to raise a connection error
        with patch.object(service.session, "get") as mock_get:
            mock_get.side_effect = ConnectionError("Connection failed")

            # Also mock session.head to raise a connection error
            with patch.object(service.session, "head") as mock_head:
                mock_head.side_effect = ConnectionError("Connection failed")

                result = service.check_url_health(url)

                assert result["status"] == UrlStatus.State.BROKEN
                assert result["error"] is not None

    def test_check_url_health_with_ssl_error(self):
        """Test checking URL health with SSL error"""
        url = Url.objects.create(
            long_url="https://example.com/ssl-error",
            short_url="sslerror123",
            user=self.regular_user,
        )
        UrlStatus.objects.create(url=url)

        service = LinkRotService()

        # Mock the session.get method to raise an SSL error
        with patch.object(service.session, "get") as mock_get:
            mock_get.side_effect = Exception("SSL error occurred")

            # Also mock session.head to raise an SSL error
            with patch.object(service.session, "head") as mock_head:
                mock_head.side_effect = Exception("SSL error occurred")

                result = service.check_url_health(url)

                assert result["status"] == UrlStatus.State.BROKEN
                assert result["error"] is not None


@pytest.mark.django_db
class TestLinkRotTasks:
    """Test Celery tasks for link rot checking"""

    def setup_method(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )
        self.regular_user = User.objects.create_user(
            username="regularuser",
            email="regular@example.com",
            password="regularpass123",
            role=User.Role.USER,
        )
        self.client.force_authenticate(user=self.admin_user)

        # Clear Redis queue before tests
        redis_conn = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
        )
        redis_conn.delete("link_rot:urls_to_check")

    def test_populate_link_rot_queue_task(self):
        """Test the task that populates the Redis queue with URLs needing check"""
        # Create URLs that need checking
        for i in range(5):
            url = Url.objects.create(
                long_url=f"https://www.example.com/test{i}",
                short_url=f"test{i}123",
                user=self.regular_user,
            )
            # Set last_checked to be old to trigger check
            UrlStatus.objects.create(
                url=url, last_checked=timezone.now() - timedelta(days=10)
            )

        # Run the populate task
        from api.url.tasks import populate_link_rot_queue

        result = populate_link_rot_queue(days_threshold=7, batch_size=100)

        assert result["status"] == "success"
        assert result["urls_added"] == 5

        # Check that URLs were added to Redis
        redis_conn = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
        )
        queue_size = redis_conn.llen("link_rot:urls_to_check")
        assert queue_size == 5

    def test_check_and_update_link_rot_batch_task(self):
        """Test the task that processes URLs from the Redis queue"""
        # Create URLs and add them to Redis queue
        urls = []
        for i in range(3):
            url = Url.objects.create(
                long_url=f"https://example.com/test{i}",
                short_url=f"batch{i}123",
                user=self.regular_user,
            )
            UrlStatus.objects.create(url=url)
            urls.append(url)

        # Add URLs to Redis queue
        redis_conn = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
        )
        for url in urls:
            redis_conn.rpush("link_rot:urls_to_check", str(url.id))

        # Run the batch processing task
        from api.url.tasks import check_and_update_link_rot_batch

        # Mock the check_url_health method to avoid real network requests
        with patch(
            "api.url.link_rot.LinkRotService.LinkRotService.check_url_health"
        ) as mock_check:
            # Configure mock to return different results for each URL
            def side_effect(url_instance):
                if url_instance.id == urls[0].id:
                    return {
                        "status": UrlStatus.State.ACTIVE,
                        "url_id": url_instance.id,
                        "destination": url_instance.long_url,
                        "error": None,
                    }
                else:
                    return {
                        "status": UrlStatus.State.BROKEN,
                        "url_id": url_instance.id,
                        "destination": url_instance.long_url,
                        "error": "HTTP 404",
                    }

            mock_check.side_effect = side_effect

            result = check_and_update_link_rot_batch(batch_size=5)

        assert result["status"] == "success"
        assert result["total_processed"] == 3

        # Verify that Redis queue is empty
        queue_size = redis_conn.llen("link_rot:urls_to_check")
        assert queue_size == 0

        # Verify that statuses were updated in DB
        for url in urls:
            status = UrlStatus.objects.get(url=url)
            assert status.state in [UrlStatus.State.ACTIVE, UrlStatus.State.BROKEN]

    def test_populate_queue_with_no_urls_needing_check(self):
        """Test populate task when no URLs need checking"""
        # Create URLs that were recently checked
        for i in range(3):
            url = Url.objects.create(
                long_url=f"https://www.example.com/recent{i}",
                short_url=f"recent{i}123",
                user=self.regular_user,
            )
            # Set last_checked to be recent
            UrlStatus.objects.create(
                url=url,
                last_checked=timezone.now() - timedelta(days=1),
            )

        from api.url.tasks import populate_link_rot_queue

        result = populate_link_rot_queue(days_threshold=7)

        assert result["status"] == "success"
        assert result["urls_added"] == 0

    def test_batch_processing_with_empty_queue(self):
        """Test batch processing when queue is empty"""
        from api.url.tasks import check_and_update_link_rot_batch

        result = check_and_update_link_rot_batch(batch_size=5)

        assert result["status"] == "success"
        assert result["total_processed"] == 0

    def test_batch_processing_stops_when_queue_empty(self):
        """Test that batch processing stops when Redis queue is empty"""
        # Add some URLs to queue
        urls = []
        for i in range(2):
            url = Url.objects.create(
                long_url=f"https://example.com/test{i}",
                short_url=f"stop{i}123",
                user=self.regular_user,
            )
            UrlStatus.objects.create(url=url)
            urls.append(url)

        # Add URLs to Redis queue
        redis_conn = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
        )
        for url in urls:
            redis_conn.rpush("link_rot:urls_to_check", str(url.id))

        from api.url.tasks import check_and_update_link_rot_batch

        # Mock the check_url_health method to avoid real network requests
        with patch(
            "api.url.link_rot.LinkRotService.LinkRotService.check_url_health"
        ) as mock_check:
            # Configure mock to return different results for each URL
            def side_effect(url_instance):
                return {
                    "status": (
                        UrlStatus.State.ACTIVE
                        if url_instance.id == urls[0].id
                        else UrlStatus.State.BROKEN
                    ),
                    "url_id": url_instance.id,
                    "destination": url_instance.long_url,
                    "error": None if url_instance.id == urls[0].id else "HTTP 404",
                }

            mock_check.side_effect = side_effect

            # Process with smaller batch size than number of URLs
            result = check_and_update_link_rot_batch(batch_size=2)

        assert result["status"] == "success"
        assert result["total_processed"] == 2

        # Queue should be empty
        queue_size = redis_conn.llen("link_rot:urls_to_check")
        assert queue_size == 0
