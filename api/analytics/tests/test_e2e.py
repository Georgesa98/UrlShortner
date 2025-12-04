import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from datetime import datetime, timedelta, timezone
from api.analytics.utils import hash_ip
from api.url.models import Url
from api.analytics.models import Visit

"""
E2E tests for Analytics endpoints
"""
User = get_user_model()


@pytest.mark.django_db
class TestTopVisitedEndpoint:
    """Test GET /api/analytics/top-visited/ endpoint"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/api/analytics/top-visited/"

    def test_top_visited_empty(self):
        """Test top visited with no URLs"""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert "top_urls" in response.data
        assert response.data["count"] == 0
        assert len(response.data["top_urls"]) == 0

    def test_top_visited_with_urls(self):
        """Test top visited with multiple URLs"""
        # Create URLs with different visit counts
        url1 = Url.objects.create(
            long_url="https://www.example.com/first",
            short_url="first123",
            user=self.user,
            visits=100,
        )
        url2 = Url.objects.create(
            long_url="https://www.example.com/second",
            short_url="second123",
            user=self.user,
            visits=50,
        )
        url3 = Url.objects.create(
            long_url="https://www.example.com/third",
            short_url="third123",
            user=self.user,
            visits=200,
        )

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3
        assert len(response.data["top_urls"]) == 3

        # Verify sorted by visits (descending)
        visits = [item["visits"] for item in response.data["top_urls"]]
        assert visits == sorted(visits, reverse=True)
        assert response.data["top_urls"][0]["visits"] == 200
        assert response.data["top_urls"][0]["short_url"] == "third123"

    def test_top_visited_only_user_urls(self):
        """Test top visited returns only authenticated user's URLs"""
        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )

        # Create URLs for both users
        user_url = Url.objects.create(
            long_url="https://www.example.com/mine",
            short_url="mine123",
            user=self.user,
            visits=100,
        )
        other_url = Url.objects.create(
            long_url="https://www.example.com/theirs",
            short_url="theirs123",
            user=other_user,
            visits=500,
        )

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        short_urls = [item["short_url"] for item in response.data["top_urls"]]
        assert "mine123" in short_urls
        assert "theirs123" not in short_urls

    def test_top_visited_response_structure(self):
        """Test top visited response contains correct fields"""
        url_obj = Url.objects.create(
            long_url="https://www.example.com/test",
            short_url="test123",
            user=self.user,
            visits=10,
        )

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["top_urls"]) == 1

        url_data = response.data["top_urls"][0]
        assert "id" in url_data
        assert "short_url" in url_data
        assert "long_url" in url_data
        assert "visits" in url_data
        assert "created_at" in url_data

    def test_top_visited_unauthenticated(self):
        """Test top visited without authentication"""
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestURLSummaryEndpoint:
    """Test GET /api/analytics/url-summary/{url_id} endpoint"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

        self.url_obj = Url.objects.create(
            long_url="https://www.example.com/analytics",
            short_url="analytics123",
            user=self.user,
            visits=50,
            unique_visits=30,
        )

    def test_url_summary_success(self):
        """Test successful Url summary retrieval"""
        url = f"/api/analytics/url-summary/{self.url_obj.id}"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "basic_info" in response.data
        assert "analytics" in response.data

        # Verify Url data
        assert response.data["basic_info"]["id"] == self.url_obj.id
        assert response.data["basic_info"]["short_url"] == self.url_obj.short_url
        assert response.data["basic_info"]["long_url"] == self.url_obj.long_url
        assert response.data["basic_info"]["visits"] == 50
        assert response.data["basic_info"]["unique_visits"] == 30

    def test_url_summary_with_days_parameter(self):
        """Test Url summary with custom days parameter"""
        url = f"/api/analytics/url-summary/{self.url_obj.id}?days=30"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_url_summary_analytics_structure(self):
        """Test Url summary analytics data structure"""
        # Create some visits
        for i in range(5):
            hashed_ip = hash_ip(f"192.168.1.{i}")
            Visit.objects.create(
                url=self.url_obj,
                hashed_ip=hashed_ip,
                referrer="https://google.com",
                device="desktop",
                new_visitor=True,
            )

        url = f"/api/analytics/url-summary/{self.url_obj.id}"
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        basic_info = response.data["basic_info"]
        analytics = response.data["analytics"]
        top_metrics = response.data["top_metrics"]

        assert "visits" in basic_info
        assert "unique_visits" in basic_info
        assert "daily_visits" in analytics
        assert "unique_vs_total" in analytics
        assert "devices" in top_metrics
        assert "browsers" in top_metrics
        assert "operating_systems" in top_metrics
        assert "countries" in top_metrics

    def test_url_summary_daily_visits_format(self):
        """Test daily visits array format"""
        hashed_ip = hash_ip("192.168.1.1")
        Visit.objects.create(
            url=self.url_obj,
            hashed_ip=hashed_ip,
        )

        url = f"/api/analytics/url-summary/{self.url_obj.id}"
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        daily_visits = response.data["analytics"]["daily_visits"]

        assert isinstance(daily_visits, list)
        if len(daily_visits) > 0:
            assert "date" in daily_visits[0]
            assert "daily_visits" in daily_visits[0]
            assert "unique_visits" in daily_visits[0]

    def test_url_summary_top_locations_format(self):
        """Test top locations array format"""
        hashed_ip = hash_ip("192.168.1.1")
        Visit.objects.create(url=self.url_obj, hashed_ip=hashed_ip, geolocation="US")

        url = f"/api/analytics/url-summary/{self.url_obj.id}"
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        top_locations = response.data["top_metrics"]["countries"]

        assert isinstance(top_locations, list)
        if len(top_locations) > 0:
            assert "geolocation" in top_locations[0]
            assert "count" in top_locations[0]

    def test_url_summary_not_owner(self):
        """Test Url summary access by non-owner"""
        self.client.force_authenticate(user=self.other_user)
        url = f"/api/analytics/url-summary/{self.url_obj.id}"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_url_summary_not_found(self):
        """Test Url summary for non-existent Url"""
        url = "/api/analytics/url-summary/99999"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_url_summary_unauthenticated(self):
        """Test Url summary without authentication"""
        self.client.force_authenticate(user=None)
        url = f"/api/analytics/url-summary/{self.url_obj.id}"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestAnalyticsIntegration:
    """Integration tests for analytics workflows"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

    def test_visit_tracking_and_analytics(self):
        """Test complete workflow: Url creation, visits, and analytics"""
        # Create Url
        create_payload = {"long_url": "https://www.example.com/track"}
        create_response = self.client.post(
            "/api/url/shorten/", create_payload, format="json"
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        short_url = create_response.data["short_url"]
        url_id = create_response.data["id"]

        # Simulate visits
        for i in range(3):
            redirect_response = self.client.get(f"/api/url/redirect/{short_url}/")
            assert redirect_response.status_code == status.HTTP_302_FOUND

        # Check top visited
        top_response = self.client.get("/api/analytics/top-visited/")
        assert top_response.status_code == status.HTTP_200_OK
        assert any(
            item["short_url"] == short_url for item in top_response.data["top_urls"]
        )

        # Check Url summary
        summary_response = self.client.get(f"/api/analytics/url-summary/{url_id}")
        assert summary_response.status_code == status.HTTP_200_OK
        assert summary_response.data["basic_info"]["visits"] >= 3

    def test_multiple_urls_analytics(self):
        """Test analytics with multiple URLs"""
        # Create multiple URLs
        urls = []
        for i in range(3):
            create_response = self.client.post(
                "/api/url/shorten/",
                {"long_url": f"https://www.example.com/url{i}"},
                format="json",
            )
            urls.append(
                {
                    "short_url": create_response.data["short_url"],
                    "id": create_response.data["id"],
                }
            )

        # Add visits to URLs with different amounts
        for idx, url_data in enumerate(urls):
            for _ in range((idx + 1) * 5):  # 5, 10, 15 visits
                self.client.get(f'/api/url/redirect/{url_data["short_url"]}/')

        # Check top visited shows correct order
        top_response = self.client.get("/api/analytics/top-visited/")
        assert top_response.status_code == status.HTTP_200_OK
        assert len(top_response.data["top_urls"]) == 3

        # Verify descending order by visits
        visits = [item["visits"] for item in top_response.data["top_urls"]]
        assert visits == sorted(visits, reverse=True)

    def test_analytics_device_breakdown(self):
        """Test device breakdown in analytics"""
        # Create Url
        create_response = self.client.post(
            "/api/url/shorten/",
            {"long_url": "https://www.example.com/devices"},
            format="json",
        )
        url_id = create_response.data["id"]
        short_url = create_response.data["short_url"]
        url_obj = Url.objects.get(short_url=short_url)

        # Create visits with different devices
        Visit.objects.create(
            url=url_obj, hashed_ip=hash_ip("192.168.1.1"), device="desktop"
        )
        Visit.objects.create(
            url=url_obj, hashed_ip=hash_ip("192.168.1.2"), device="mobile"
        )
        Visit.objects.create(
            url=url_obj, hashed_ip=hash_ip("192.168.1.3"), device="desktop"
        )

        # Get analytics
        summary_response = self.client.get(f"/api/analytics/url-summary/{url_id}")
        assert summary_response.status_code == status.HTTP_200_OK

        device_breakdown = summary_response.data["top_metrics"]["devices"]
        assert (
            device_breakdown[0]["device"] == "desktop"
            and device_breakdown[0]["count"] >= 2
        )
        assert (
            device_breakdown[1]["device"] == "mobile"
            and device_breakdown[1]["count"] >= 1
        )

    def test_analytics_time_range(self):
        """Test analytics with different time ranges"""
        # Create Url
        create_response = self.client.post(
            "/api/url/shorten/",
            {"long_url": "https://www.example.com/timerange"},
            format="json",
        )
        url_id = create_response.data["id"]
        short_url = create_response.data["short_url"]
        url_obj = Url.objects.get(short_url=short_url)

        # Create visits at different times
        Visit.objects.create(
            url=url_obj,
            hashed_ip=hash_ip("192.168.1.1"),
            timestamp=datetime.now(timezone.utc),
        )
        Visit.objects.create(
            url=url_obj,
            hashed_ip=hash_ip("192.168.1.2"),
            timestamp=datetime.now(timezone.utc) - timedelta(days=5),
        )
        Visit.objects.create(
            url=url_obj,
            hashed_ip=hash_ip("192.168.1.3"),
            timestamp=datetime.now(timezone.utc) - timedelta(days=10),
        )

        # Get 7-day analytics
        response_7days = self.client.get(f"/api/analytics/url-summary/{url_id}?days=7")
        assert response_7days.status_code == status.HTTP_200_OK

        # Get 30-day analytics
        response_30days = self.client.get(
            f"/api/analytics/url-summary/{url_id}?days=30"
        )
        assert response_30days.status_code == status.HTTP_200_OK

        # 30-day should have more or equal visits than 7-day
        total_7 = response_7days.data["analytics"]["unique_vs_total"]["total"]
        total_30 = response_30days.data["analytics"]["unique_vs_total"]["total"]
        assert total_30 >= total_7
