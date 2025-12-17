from django.test import TestCase
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
import redis
from datetime import datetime, timezone
from api.url.services.BurstProtectionService import (
    BurstProtectionService,
    get_burst_protection_service,
)
from api.url.models import Url, UrlStatus


class BurstProtectionServiceTest(TestCase):
    """Test suite for BurstProtectionService"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        # Create a fresh instance for each test
        self.service = BurstProtectionService()

        # Test data
        self.test_ip = "192.168.1.1"
        self.test_short_url = "abc123"
        self.test_timestamp = datetime.now(timezone.utc).timestamp()

        # Clear Redis data before each test
        self.service.redis_client.flushdb()

        # Create test Url and UrlStatus objects
        self.url = Url.objects.create(
            short_url=self.test_short_url,
            long_url="https://example.com",
        )
        self.url_status = UrlStatus.objects.create(
            url=self.url,
            state=UrlStatus.State.ACTIVE,
        )

    def tearDown(self):
        """Clean up after each test"""
        self.service.redis_client.flushdb()

    # ==================== Test Initialization ====================

    def test_service_initialization(self):
        """Test that service initializes with correct default thresholds"""
        self.assertIsNotNone(self.service.redis_client)
        self.assertEqual(self.service.default_thresholds["short_term_window"], 10)
        self.assertEqual(self.service.default_thresholds["short_term_limit"], 10)
        self.assertEqual(self.service.default_thresholds["medium_term_window"], 60)
        self.assertEqual(self.service.default_thresholds["medium_term_limit"], 50)
        self.assertEqual(self.service.default_thresholds["long_term_window"], 3600)
        self.assertEqual(self.service.default_thresholds["long_term_limit"], 1000)

    def test_singleton_pattern(self):
        """Test that get_burst_protection_service returns singleton instance"""
        service1 = get_burst_protection_service()
        service2 = get_burst_protection_service()
        self.assertIs(service1, service2)

    # ==================== Test _track_click ====================

    def test_track_click_adds_to_redis(self):
        """Test that tracking a click adds entries to Redis"""
        self.service._track_click(self.test_short_url, self.test_ip)

        url_key = f"burst_protection:url:{self.test_short_url}"
        ip_key = f"burst_protection:ip:{self.test_ip}"

        # Check that entries were added
        url_count = self.service.redis_client.zcard(url_key)
        ip_count = self.service.redis_client.zcard(ip_key)

        self.assertEqual(url_count, 1)
        self.assertEqual(ip_count, 1)

    def test_track_click_multiple_requests(self):
        """Test tracking multiple clicks increments count"""
        for _ in range(5):
            self.service._track_click(self.test_short_url, self.test_ip)

        url_key = f"burst_protection:url:{self.test_short_url}"
        ip_key = f"burst_protection:ip:{self.test_ip}"

        url_count = self.service.redis_client.zcard(url_key)
        ip_count = self.service.redis_client.zcard(ip_key)

        self.assertEqual(url_count, 5)
        self.assertEqual(ip_count, 5)

    def test_track_click_cleanup_old_entries(self):
        """Test that old entries beyond long_term_window are cleaned up"""
        url_key = f"burst_protection:url:{self.test_short_url}"

        # Add old entry (beyond long_term_window)
        old_timestamp = self.test_timestamp - 7200  # 2 hours ago
        self.service.redis_client.zadd(
            url_key, {f"request_{old_timestamp}": old_timestamp}
        )

        # Track a new click (should trigger cleanup)
        self.service._track_click(self.test_short_url, self.test_ip)

        # Old entry should be removed
        count = self.service.redis_client.zcard(url_key)
        self.assertEqual(count, 1)  # Only the new entry

    # ==================== Test _check_window_burst ====================

    def test_check_window_burst_below_threshold(self):
        """Test that requests below threshold don't trigger burst detection"""
        ip_key = f"burst_protection:ip:{self.test_ip}"

        # Add 5 requests (below short_term_limit of 10)
        for i in range(5):
            timestamp = self.test_timestamp - i
            self.service.redis_client.zadd(ip_key, {f"request_{timestamp}": timestamp})

        start_time = self.test_timestamp - 10
        is_burst = self.service._check_window_burst(ip_key, start_time, 10)

        self.assertFalse(is_burst)

    def test_check_window_burst_at_threshold(self):
        """Test that requests at threshold trigger burst detection"""
        ip_key = f"burst_protection:ip:{self.test_ip}"

        # Add exactly 10 requests
        for i in range(10):
            timestamp = self.test_timestamp - i
            self.service.redis_client.zadd(ip_key, {f"request_{timestamp}": timestamp})

        start_time = self.test_timestamp - 10
        is_burst = self.service._check_window_burst(ip_key, start_time, 10)

        self.assertTrue(is_burst)

    def test_check_window_burst_above_threshold(self):
        """Test that requests above threshold trigger burst detection"""
        ip_key = f"burst_protection:ip:{self.test_ip}"

        # Add 15 requests (above short_term_limit of 10)
        for i in range(15):
            timestamp = self.test_timestamp - i
            self.service.redis_client.zadd(ip_key, {f"request_{timestamp}": timestamp})

        start_time = self.test_timestamp - 10
        is_burst = self.service._check_window_burst(ip_key, start_time, 10)

        self.assertTrue(is_burst)

    # ==================== Test _detect_burst ====================

    def test_detect_burst_no_burst(self):
        """Test that normal traffic doesn't trigger burst detection"""
        # Add just a few requests
        for _ in range(3):
            self.service._track_click(self.test_short_url, self.test_ip)

        is_burst = self.service._detect_burst(self.test_ip, self.test_short_url)
        self.assertFalse(is_burst)

    def test_detect_burst_short_term_ip(self):
        """Test burst detection for IP in short term window"""
        ip_key = f"burst_protection:ip:{self.test_ip}"

        # Add 10 requests in short window (triggers short_term_limit)
        for i in range(10):
            timestamp = self.test_timestamp - i
            self.service.redis_client.zadd(ip_key, {f"request_{timestamp}": timestamp})

        is_burst = self.service._detect_burst(self.test_ip, self.test_short_url)
        self.assertTrue(is_burst)

    def test_detect_burst_short_term_url(self):
        """Test burst detection for Url in short term window"""
        url_key = f"burst_protection:url:{self.test_short_url}"

        # Add 10 requests in short window
        for i in range(10):
            timestamp = self.test_timestamp - i
            self.service.redis_client.zadd(url_key, {f"request_{timestamp}": timestamp})

        is_burst = self.service._detect_burst(self.test_ip, self.test_short_url)
        self.assertTrue(is_burst)

    def test_detect_burst_medium_term_ip(self):
        """Test burst detection for IP in medium term window"""
        ip_key = f"burst_protection:ip:{self.test_ip}"

        # Add 50 requests in medium window (triggers medium_term_limit)
        for i in range(50):
            timestamp = self.test_timestamp - (i * 1.2)  # Spread over 60 seconds
            self.service.redis_client.zadd(ip_key, {f"request_{timestamp}": timestamp})

        is_burst = self.service._detect_burst(self.test_ip, self.test_short_url)
        self.assertTrue(is_burst)

    def test_detect_burst_medium_term_url(self):
        """Test burst detection for Url in medium term window"""
        url_key = f"burst_protection:url:{self.test_short_url}"

        # Add 50 requests in medium window
        for i in range(50):
            timestamp = self.test_timestamp - (i * 1.2)
            self.service.redis_client.zadd(url_key, {f"request_{timestamp}": timestamp})

        is_burst = self.service._detect_burst(self.test_ip, self.test_short_url)
        self.assertTrue(is_burst)

    def test_detect_burst_long_term_ip(self):
        """Test burst detection for IP in long term window"""
        ip_key = f"burst_protection:ip:{self.test_ip}"

        # Add 1000 requests in long window (triggers long_term_limit)
        for i in range(1000):
            timestamp = self.test_timestamp - (i * 3.6)  # Spread over 3600 seconds
            self.service.redis_client.zadd(ip_key, {f"request_{timestamp}": timestamp})

        is_burst = self.service._detect_burst(self.test_ip, self.test_short_url)
        self.assertTrue(is_burst)

    def test_detect_burst_outside_window(self):
        """Test that old requests outside window don't trigger burst"""
        ip_key = f"burst_protection:ip:{self.test_ip}"

        # Add 10 requests but outside the short_term_window
        for i in range(10):
            old_timestamp = self.test_timestamp - 100 - i  # More than 10 seconds ago
            self.service.redis_client.zadd(
                ip_key, {f"request_{old_timestamp}": old_timestamp}
            )

        is_burst = self.service._detect_burst(self.test_ip, self.test_short_url)
        self.assertFalse(is_burst)

    # ==================== Test _flag_url ====================

    def test_flag_url_success(self):
        """Test that Url is successfully flagged"""
        self.service._flag_url(self.test_short_url, self.test_ip)

        self.url_status.refresh_from_db()
        self.assertEqual(self.url_status.state, UrlStatus.State.FLAGGED)
        self.assertEqual(self.url_status.reason, "Too many requests on the url")

    def test_flag_url_already_flagged(self):
        """Test that already flagged Url doesn't get re-flagged unnecessarily"""
        # Flag it first time
        self.service._flag_url(self.test_short_url, self.test_ip)

        # Try to flag again
        self.service._flag_url(self.test_short_url, self.test_ip)

        self.url_status.refresh_from_db()
        self.assertEqual(self.url_status.state, UrlStatus.State.FLAGGED)

    def test_flag_url_not_found(self):
        """Test handling of non-existent Url"""
        with self.assertRaises(Url.DoesNotExist):
            self.service._flag_url("nonexistent", self.test_ip)

    def test_flag_url_status_not_found(self):
        """Test handling of missing UrlStatus"""
        # Delete the UrlStatus
        self.url_status.delete()

        with self.assertRaises(UrlStatus.DoesNotExist):
            self.service._flag_url(self.test_short_url, self.test_ip)

    def test_flag_url_changes_from_active_to_flagged(self):
        """Test that Url state changes from ACTIVE to FLAGGED"""
        # Ensure Url is active
        self.assertEqual(self.url_status.state, UrlStatus.State.ACTIVE)

        # Flag the Url
        self.service._flag_url(self.test_short_url, self.test_ip)

        # Verify state changed
        self.url_status.refresh_from_db()
        self.assertEqual(self.url_status.state, UrlStatus.State.FLAGGED)

    def test_flag_url_sets_reason(self):
        """Test that flagging sets appropriate reason"""
        self.service._flag_url(self.test_short_url, self.test_ip)

        self.url_status.refresh_from_db()
        self.assertIsNotNone(self.url_status.reason)
        self.assertIn("Too many requests", self.url_status.reason)

    # ==================== Test check_burst (Integration) ====================

    @patch("redis.lock.Lock")
    def test_check_burst_lock_acquired_no_burst(self, mock_lock_class):
        """Test successful request when lock acquired and no burst detected"""
        # Mock lock
        mock_lock = MagicMock()
        mock_lock.acquire.return_value = True
        mock_lock_class.return_value = mock_lock

        result = self.service.check_burst(self.test_ip, self.test_short_url)

        self.assertTrue(result)
        mock_lock.acquire.assert_called_once_with(blocking=True)
        mock_lock.release.assert_called_once()

        # Check that click was tracked
        ip_key = f"burst_protection:ip:{self.test_ip}"
        count = self.service.redis_client.zcard(ip_key)
        self.assertGreater(count, 0)

    @patch("redis.lock.Lock")
    def test_check_burst_lock_acquired_burst_detected(self, mock_lock_class):
        """Test request blocked when burst detected"""
        # Mock lock
        mock_lock = MagicMock()
        mock_lock.acquire.return_value = True
        mock_lock_class.return_value = mock_lock

        # Add enough requests to trigger burst
        ip_key = f"burst_protection:ip:{self.test_ip}"
        for i in range(10):
            timestamp = self.test_timestamp - i
            self.service.redis_client.zadd(ip_key, {f"request_{timestamp}": timestamp})

        result = self.service.check_burst(self.test_ip, self.test_short_url)

        self.assertFalse(result)

        # Check that Url was flagged
        self.url_status.refresh_from_db()
        self.assertEqual(self.url_status.state, UrlStatus.State.FLAGGED)

    @patch("redis.lock.Lock")
    def test_check_burst_lock_not_acquired(self, mock_lock_class):
        """Test request blocked when lock cannot be acquired"""
        # Mock lock acquisition failure
        mock_lock = MagicMock()
        mock_lock.acquire.return_value = False
        mock_lock_class.return_value = mock_lock

        result = self.service.check_burst(self.test_ip, self.test_short_url)

        self.assertFalse(result)
        mock_lock.acquire.assert_called_once_with(blocking=True)
        mock_lock.release.assert_not_called()

    @patch("redis.lock.Lock")
    def test_check_burst_lock_released_on_exception(self, mock_lock_class):
        """Test that lock is released even when exception occurs"""
        # Mock lock
        mock_lock = MagicMock()
        mock_lock.acquire.return_value = True
        mock_lock_class.return_value = mock_lock

        # Make _detect_burst raise an exception
        with patch.object(
            self.service, "_detect_burst", side_effect=Exception("Test error")
        ):
            result = self.service.check_burst(self.test_ip, self.test_short_url)

        self.assertFalse(result)
        mock_lock.release.assert_called_once()

    # ==================== Test Race Conditions ====================

    def test_concurrent_requests_same_ip(self):
        """Test that multiple concurrent requests from same IP are handled correctly"""
        from threading import Thread

        results = []

        def make_request():
            result = self.service.check_burst(self.test_ip, self.test_short_url)
            results.append(result)

        # Simulate 5 concurrent requests
        threads = [Thread(target=make_request) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # At least some should succeed
        self.assertTrue(any(results))

    def test_different_ips_different_urls(self):
        """Test that different IPs and URLs are tracked independently"""
        ip1 = "192.168.1.1"
        ip2 = "192.168.1.2"
        url1 = "abc123"
        url2 = "def456"

        # Create second Url
        url_obj2 = Url.objects.create(short_url=url2, long_url="https://example2.com")
        UrlStatus.objects.create(url=url_obj2, state=UrlStatus.State.ACTIVE)

        # Track clicks for different combinations
        for _ in range(5):
            self.service._track_click(url1, ip1)
            self.service._track_click(url2, ip2)

        # Check that they're tracked separately
        ip1_key = f"burst_protection:ip:{ip1}"
        ip2_key = f"burst_protection:ip:{ip2}"
        url1_key = f"burst_protection:url:{url1}"
        url2_key = f"burst_protection:url:{url2}"

        self.assertEqual(self.service.redis_client.zcard(ip1_key), 5)
        self.assertEqual(self.service.redis_client.zcard(ip2_key), 5)
        self.assertEqual(self.service.redis_client.zcard(url1_key), 5)
        self.assertEqual(self.service.redis_client.zcard(url2_key), 5)

    # ==================== Test Edge Cases ====================

    def test_empty_ip(self):
        """Test handling of empty IP address"""
        result = self.service.check_burst("", self.test_short_url)
        # Should still work, just with empty string as key
        self.assertIsInstance(result, bool)

    def test_empty_short_url(self):
        """Test handling of empty short Url"""
        # This will raise Url.DoesNotExist when trying to flag
        ip_key = f"burst_protection:ip:{self.test_ip}"

        # Add enough requests to trigger burst
        for i in range(10):
            timestamp = self.test_timestamp - i
            self.service.redis_client.zadd(ip_key, {f"request_{timestamp}": timestamp})

        # Should return False due to exception handling
        result = self.service.check_burst(self.test_ip, "")
        self.assertFalse(result)

    def test_special_characters_in_keys(self):
        """Test handling of special characters in IP and Url"""
        special_ip = "192.168.1.1:8080"
        special_url = "abc-123_test"

        # Create Url with special characters
        url_obj = Url.objects.create(
            short_url=special_url, long_url="https://example.com"
        )
        UrlStatus.objects.create(url=url_obj, state=UrlStatus.State.ACTIVE)

        self.service._track_click(special_url, special_ip)

        ip_key = f"burst_protection:ip:{special_ip}"
        count = self.service.redis_client.zcard(ip_key)
        self.assertEqual(count, 1)

    def test_url_with_user(self):
        """Test burst protection works with URLs that have associated users"""
        from django.contrib.auth import get_user_model

        User = get_user_model()

        user = User.objects.create_user(username="testuser", password="testpass")
        url_with_user = Url.objects.create(
            short_url="user123", long_url="https://userurl.com", user=user
        )
        UrlStatus.objects.create(url=url_with_user, state=UrlStatus.State.ACTIVE)

        self.service._track_click("user123", self.test_ip)

        ip_key = f"burst_protection:ip:{self.test_ip}"
        count = self.service.redis_client.zcard(ip_key)
        self.assertEqual(count, 1)

    def test_url_with_expiry_date(self):
        """Test burst protection works with URLs that have expiry dates"""
        from datetime import timedelta

        future_date = datetime.now(timezone.utc) + timedelta(days=7)
        url_with_expiry = Url.objects.create(
            short_url="expiry123",
            long_url="https://expiryurl.com",
            expiry_date=future_date,
        )
        UrlStatus.objects.create(url=url_with_expiry, state=UrlStatus.State.ACTIVE)

        self.service._track_click("expiry123", self.test_ip)

        ip_key = f"burst_protection:ip:{self.test_ip}"
        count = self.service.redis_client.zcard(ip_key)
        self.assertEqual(count, 1)


class BurstProtectionIntegrationTest(TestCase):
    """Integration tests for full burst protection workflow"""

    def setUp(self):
        self.service = BurstProtectionService()
        self.service.redis_client.flushdb()
        self.test_ip = "10.0.0.1"
        self.test_short_url = "test123"

        self.url = Url.objects.create(
            short_url=self.test_short_url,
            long_url="https://test.com",
        )
        self.url_status = UrlStatus.objects.create(
            url=self.url,
            state=UrlStatus.State.ACTIVE,
        )

    def tearDown(self):
        self.service.redis_client.flushdb()

    def test_gradual_traffic_increase(self):
        """Test that gradual traffic increase is handled correctly"""
        # Send 9 requests (below threshold)
        for _ in range(9):
            result = self.service.check_burst(self.test_ip, self.test_short_url)
            self.assertTrue(result)

        # 10th request should still be OK (at threshold but not over)
        result = self.service.check_burst(self.test_ip, self.test_short_url)
        self.assertTrue(result)

        # 11th request triggers burst
        result = self.service.check_burst(self.test_ip, self.test_short_url)
        self.assertFalse(result)

        # Url should be flagged
        self.url_status.refresh_from_db()
        self.assertEqual(self.url_status.state, UrlStatus.State.FLAGGED)

    def test_burst_recovery_after_time_window(self):
        """Test that burst status can recover after time window passes"""
        # Trigger burst
        for _ in range(11):
            self.service._track_click(self.test_short_url, self.test_ip)

        is_burst = self.service._detect_burst(self.test_ip, self.test_short_url)
        self.assertTrue(is_burst)

        # Clear Redis to simulate time passing
        self.service.redis_client.flushdb()

        # Should no longer detect burst
        is_burst = self.service._detect_burst(self.test_ip, self.test_short_url)
        self.assertFalse(is_burst)

    def test_url_visits_not_affected_by_burst_protection(self):
        """Test that burst protection doesn't interfere with Url visit counting"""
        initial_visits = self.url.visits

        # Make some requests
        for _ in range(5):
            self.service.check_burst(self.test_ip, self.test_short_url)

        # Url visits should not be modified by burst protection service
        self.url.refresh_from_db()
        self.assertEqual(self.url.visits, initial_visits)

    def test_multiple_urls_same_ip(self):
        """Test that one Url getting flagged doesn't affect other URLs"""
        # Create second Url
        url2 = Url.objects.create(short_url="test456", long_url="https://test2.com")
        url_status2 = UrlStatus.objects.create(url=url2, state=UrlStatus.State.ACTIVE)

        # Trigger burst on first Url
        ip_key = f"burst_protection:ip:{self.test_ip}"
        for i in range(10):
            timestamp = datetime.now(timezone.utc).timestamp() - i
            self.service.redis_client.zadd(ip_key, {f"request_{timestamp}": timestamp})

        result1 = self.service.check_burst(self.test_ip, self.test_short_url)
        self.assertFalse(result1)

        # First Url should be flagged
        self.url_status.refresh_from_db()
        self.assertEqual(self.url_status.state, UrlStatus.State.FLAGGED)

        # Second Url should still be active
        url_status2.refresh_from_db()
        self.assertEqual(url_status2.state, UrlStatus.State.ACTIVE)

    def test_different_states_handling(self):
        """Test burst protection behavior with different Url states"""
        # Test with EXPIRED state
        self.url_status.state = UrlStatus.State.EXPIRED
        self.url_status.save()

        result = self.service.check_burst(self.test_ip, self.test_short_url)
        # Should still work - burst protection is independent of Url state
        self.assertIsInstance(result, bool)

        # Test with DISABLED state
        self.url_status.state = UrlStatus.State.DISABLED
        self.url_status.save()

        result = self.service.check_burst(self.test_ip, self.test_short_url)
        self.assertIsInstance(result, bool)
