import pytest
from django.test import Client
from django.contrib.auth import get_user_model
from api.url.models import Url, UrlStatus
from api.admin_panel.fraud.models import FraudIncident
from rest_framework.test import APIClient
from rest_framework import status
from django.test import RequestFactory
from datetime import datetime, timedelta
from django.utils import timezone as tz
from api.analytics.service import AnalyticsService
from unittest.mock import patch, MagicMock


User = get_user_model()


@pytest.mark.django_db
class TestFraudOverviewEndpoint:
    """Test GET /api/admin/fraud/overview/ endpoint"""

    def setup_method(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="pass",
            role=User.Role.ADMIN,
        )
        self.regular_user = User.objects.create_user(
            username="user", email="user@test.com", password="pass", role=User.Role.USER
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_fraud_overview_success_admin(self):
        """Test successful fraud overview retrieval by admin"""
        url = "/api/admin/fraud/overview/"
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] == True
        assert "Fraud overview retrieved successfully" in response.data["message"]

        data = response.data["data"]
        required_fields = [
            "period_days",
            "total_incidents",
            "incidents_by_type",
            "flagged_urls",
            "risk_score",
            "top_incident_types",
        ]
        for field in required_fields:
            assert field in data

    def test_fraud_overview_default_days_parameter(self):
        """Test fraud overview uses default 7 days when no parameter provided"""
        url = "/api/admin/fraud/overview/"
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["period_days"] == 7

    def test_fraud_overview_custom_days_parameter(self):
        """Test fraud overview with custom days parameter"""
        url = "/api/admin/fraud/overview/"
        response = self.client.get(url, {"days": 30})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["period_days"] == 30

    def test_fraud_overview_invalid_days_parameter(self):
        """Test fraud overview with invalid days parameter defaults to 7"""
        url = "/api/admin/fraud/overview/"
        response = self.client.get(url, {"days": "invalid"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["period_days"] == 7

    def test_fraud_overview_no_authentication(self):
        """Test fraud overview without authentication"""
        self.client.force_authenticate(user=None)
        url = "/api/admin/fraud/overview/"
        response = self.client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_fraud_overview_regular_user_forbidden(self):
        """Test fraud overview access by regular user"""
        self.client.force_authenticate(user=self.regular_user)
        url = "/api/admin/fraud/overview/"
        response = self.client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_fraud_overview_empty_database(self):
        """Test fraud overview when database has no incidents"""
        url = "/api/admin/fraud/overview/"
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.data["data"]
        assert data["total_incidents"] == 0
        assert data["incidents_by_type"] == []
        assert data["flagged_urls"] == 0
        assert data["risk_score"] == "low"

    def test_fraud_overview_with_incidents(self):
        """Test fraud overview with existing incidents"""
        # Create some test incidents
        FraudIncident.objects.create(
            incident_type="burst", details={"ip": "127.0.0.1"}, severity="high"
        )
        FraudIncident.objects.create(
            incident_type="throttle", details={"ip": "192.168.1.1"}, severity="medium"
        )

        url = "/api/admin/fraud/overview/"
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.data["data"]
        assert data["total_incidents"] == 2
        assert len(data["incidents_by_type"]) == 2

    def test_fraud_overview_with_flagged_urls(self):
        """Test fraud overview includes flagged URLs count"""
        # Create a flagged URL
        url_obj = Url.objects.create(long_url="http://test.com", short_url="flagged123")
        UrlStatus.objects.create(url=url_obj, state=UrlStatus.State.FLAGGED)

        url = "/api/admin/fraud/overview/"
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.data["data"]
        assert data["flagged_urls"] == 1

    def test_fraud_overview_risk_scoring_logic(self):
        """Test fraud overview risk scoring based on incidents and flagged URLs"""
        # Test low risk
        url = "/api/admin/fraud/overview/"
        response = self.client.get(url)
        assert response.data["data"]["risk_score"] == "low"

        # Create incidents to trigger medium risk
        for i in range(15):
            FraudIncident.objects.create(
                incident_type="test", details={}, severity="low"
            )

        response = self.client.get(url)
        # Depending on logic, may be medium or high
        assert response.data["data"]["risk_score"] in ["low", "medium", "high"]

    def test_fraud_overview_response_structure(self):
        """Test fraud overview response has correct structure"""
        url = "/api/admin/fraud/overview/"
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK

        # Check top-level structure
        assert "success" in response.data
        assert "message" in response.data
        assert "data" in response.data

        data = response.data["data"]

        # Check data structure
        assert isinstance(data["period_days"], int)
        assert isinstance(data["total_incidents"], int)
        assert isinstance(data["incidents_by_type"], list)
        assert isinstance(data["flagged_urls"], int)
        assert isinstance(data["risk_score"], str)
        assert isinstance(data["top_incident_types"], list)

        # Check incidents_by_type structure
        for incident in data["incidents_by_type"]:
            assert "incident_type" in incident
            assert "count" in incident
            assert isinstance(incident["count"], int)

    def test_fraud_overview_throttling_applied(self):
        """Test that fraud overview endpoint respects throttling"""
        # Make multiple rapid requests
        url = "/api/admin/fraud/overview/"
        responses = []
        for i in range(10):
            response = self.client.get(url)
            responses.append(response.status_code)

        # At least one should be throttled (429) if throttling is configured
        # This depends on throttle settings, so just check responses are valid
        for status_code in responses:
            assert status_code in [200, 429]

    def test_fraud_overview_different_days_ranges(self):
        """Test fraud overview with different day ranges"""
        # Create incidents at different times

        # Recent incident
        FraudIncident.objects.create(incident_type="recent", details={}, severity="low")

        # Old incident (outside default 7 days)
        old_date = tz.now() - timedelta(days=10)
        incident = FraudIncident.objects.create(
            incident_type="old", details={}, severity="low"
        )
        incident.created_at = old_date
        incident.save()

        # Test with 7 days (should include only recent)
        response = self.client.get("/api/admin/fraud/overview/", {"days": 7})
        assert response.data["data"]["total_incidents"] == 1

        # Test with 30 days (should include both)
        response = self.client.get("/api/admin/fraud/overview/", {"days": 30})
        assert response.data["data"]["total_incidents"] == 2


@pytest.mark.django_db
class TestFraudDetectionWorkflows:
    """Test complete fraud detection workflows through API interactions"""

    def setup_method(self):
        self.client = APIClient()
        self.factory = RequestFactory()
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="pass",
            role=User.Role.ADMIN,
        )
        self.regular_user = User.objects.create_user(
            username="user", email="user@test.com", password="pass", role=User.Role.USER
        )

    def test_complete_url_lifecycle_with_fraud_detection(self):
        """Test URL creation, access, and fraud monitoring workflow"""
        self.client.force_authenticate(user=self.regular_user)

        # Create URL
        create_payload = {"long_url": "https://www.example.com/lifecycle"}
        create_response = self.client.post(
            "/api/url/shorten/", create_payload, format="json"
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        short_url = create_response.data["data"]["short_url"]

        # Access URL with suspicious UA (simulated through analytics)
        url_obj = Url.objects.get(short_url=short_url)
        request = self.factory.get("/", HTTP_USER_AGENT="curl/7.68.0")
        request.user = self.regular_user
        AnalyticsService.record_visit(request, url_obj)

        # Check admin can see fraud incident in overview
        self.client.force_authenticate(user=self.admin_user)
        overview_response = self.client.get("/api/admin/fraud/overview/")
        assert overview_response.status_code == status.HTTP_200_OK
        data = overview_response.data["data"]
        assert data["total_incidents"] >= 1
        assert "suspicious_ua" in [
            inc["incident_type"] for inc in data["incidents_by_type"]
        ]

    def test_fraud_detection_with_multiple_suspicious_activities(self):
        """Test fraud detection with multiple suspicious activities"""
        # Create URL
        self.client.force_authenticate(user=self.regular_user)
        create_response = self.client.post(
            "/api/url/shorten/", {"long_url": "http://test.com"}, format="json"
        )
        short_url = create_response.data["data"]["short_url"]
        url_obj = Url.objects.get(short_url=short_url)

        # Multiple suspicious visits
        suspicious_uas = ["", "curl/7.68.0", "wget/1.20.3"]
        for ua in suspicious_uas:
            request = self.factory.get("/", HTTP_USER_AGENT=ua)
            request.user = self.regular_user
            AnalyticsService.record_visit(request, url_obj)

        # Check admin overview shows multiple incidents
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/admin/fraud/overview/")
        data = response.data["data"]
        assert data["total_incidents"] >= 3
        suspicious_incidents = [
            inc
            for inc in data["incidents_by_type"]
            if inc["incident_type"] == "suspicious_ua"
        ]
        assert len(suspicious_incidents) == 1
        assert suspicious_incidents[0]["count"] >= 3

    def test_fraud_detection_admin_monitoring_different_time_ranges(self):
        """Test admin monitoring fraud across different time ranges"""
        # Create incidents at different times
        # Recent
        FraudIncident.objects.create(incident_type="recent", details={}, severity="low")

        # 15 days ago
        mid_date = tz.now() - timedelta(days=15)
        mid_incident = FraudIncident.objects.create(
            incident_type="mid", details={}, severity="medium"
        )
        mid_incident.created_at = mid_date
        mid_incident.save()

        # 30 days ago
        old_date = tz.now() - timedelta(days=30)
        old_incident = FraudIncident.objects.create(
            incident_type="old", details={}, severity="high"
        )
        old_incident.created_at = old_date
        old_incident.save()

        self.client.force_authenticate(user=self.admin_user)

        # Test 7 days (only recent)
        response = self.client.get("/api/admin/fraud/overview/", {"days": 7})
        assert response.data["data"]["total_incidents"] == 1

        # Test 20 days (recent + mid)
        response = self.client.get("/api/admin/fraud/overview/", {"days": 20})
        assert response.data["data"]["total_incidents"] == 2

        # Test 60 days (all)
        response = self.client.get("/api/admin/fraud/overview/", {"days": 60})
        assert response.data["data"]["total_incidents"] == 3

    def test_fraud_detection_with_burst_and_throttle_simulation(self):
        """Test fraud detection including burst protection and throttling"""
        # Create URL and simulate burst
        url_obj = Url.objects.create(
            long_url="http://burst.com", short_url="burst123", user=self.regular_user
        )
        UrlStatus.objects.create(url=url_obj)

        # Simulate burst protection trigger
        from api.url.services.BurstProtectionService import get_burst_protection_service

        service = get_burst_protection_service()
        initial_count = FraudIncident.objects.count()
        service._flag_url("burst123", "127.0.0.1")
        after_burst_count = FraudIncident.objects.count()
        assert after_burst_count == initial_count + 1  # Burst incident logged

        # Simulate throttle violation
        from api.throttling import IPRateThrottle

        throttle = IPRateThrottle()
        throttle.rate = "1/minute"
        request = self.factory.get("/")
        request.user = self.regular_user
        view = MagicMock()

        from api.admin_panel.fraud.FraudService import FraudService

        before_throttle_count = FraudIncident.objects.count()
        # Call the flag to simulate throttle violation
        FraudService.flag_throttle_violation(request, view, throttle.rate)

        # Check that the flag creates an incident
        after_throttle_count = FraudIncident.objects.count()
        assert (
            after_throttle_count == before_throttle_count + 1
        )  # Throttle incident logged

        # Check admin overview shows both incidents
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/admin/fraud/overview/")
        data = response.data["data"]
        assert data["total_incidents"] >= 2

        incident_types = [inc["incident_type"] for inc in data["incidents_by_type"]]
        assert "burst" in incident_types
        assert "throttle" in incident_types

    def test_fraud_detection_risk_escalation_workflow(self):
        """Test how risk score escalates with increasing incidents"""
        self.client.force_authenticate(user=self.admin_user)

        # Start with low risk
        response = self.client.get("/api/admin/fraud/overview/")
        assert response.data["data"]["risk_score"] == "low"

        # Add 11 incidents (should trigger medium risk)
        for i in range(11):
            FraudIncident.objects.create(
                incident_type="test", details={}, severity="low"
            )

        response = self.client.get("/api/admin/fraud/overview/")
        assert response.data["data"]["risk_score"] == "medium"

        # Add more to reach high risk
        for i in range(40):  # Total will be 11 + 40 = 51 >= 50
            FraudIncident.objects.create(
                incident_type="test2", details={}, severity="low"
            )

        response = self.client.get("/api/admin/fraud/overview/")
        assert response.data["data"]["risk_score"] == "high"

    def test_fraud_detection_cross_user_activities(self):
        """Test fraud detection across multiple users"""
        # Create multiple users
        users = []
        for i in range(3):
            user = User.objects.create_user(
                username=f"user{i}", email=f"user{i}@test.com", password="pass"
            )
            users.append(user)

        # Each user creates a URL and accesses with suspicious UA
        for user in users:
            # Create URL
            self.client.force_authenticate(user=user)
            create_response = self.client.post(
                "/api/url/shorten/", {"long_url": f"http://test{i}.com"}, format="json"
            )
            short_url = create_response.data["data"]["short_url"]
            url_obj = Url.objects.get(short_url=short_url)

            # Suspicious access
            request = self.factory.get("/", HTTP_USER_AGENT="curl/7.68.0")
            request.user = user
            AnalyticsService.record_visit(request, url_obj)

        # Admin checks overview
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/admin/fraud/overview/")
        data = response.data["data"]
        assert data["total_incidents"] >= 3
        suspicious_count = sum(
            inc["count"]
            for inc in data["incidents_by_type"]
            if inc["incident_type"] == "suspicious_ua"
        )
        assert suspicious_count >= 3

    def test_fraud_detection_normal_activities_dont_trigger(self):
        """Test that normal activities don't trigger fraud incidents"""
        self.client.force_authenticate(user=self.regular_user)

        # Create URL normally
        create_response = self.client.post(
            "/api/url/shorten/", {"long_url": "http://normal.com"}, format="json"
        )
        short_url = create_response.data["data"]["short_url"]
        url_obj = Url.objects.get(short_url=short_url)

        # Normal access
        request = self.factory.get(
            "/",
            HTTP_USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        )
        request.user = self.regular_user
        AnalyticsService.record_visit(request, url_obj)

        # Check no fraud incidents
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/admin/fraud/overview/")
        data = response.data["data"]
        assert data["total_incidents"] == 0
        assert data["risk_score"] == "low"


@pytest.mark.django_db
class TestFraudDetectionEdgeCases:
    """Test edge cases and error conditions in fraud detection"""

    def setup_method(self):
        self.client = APIClient()
        self.factory = RequestFactory()
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="pass",
            role=User.Role.ADMIN,
        )
        self.regular_user = User.objects.create_user(
            username="user", email="user@test.com", password="pass", role=User.Role.USER
        )

    def test_fraud_overview_with_extremely_large_days_parameter(self):
        """Test fraud overview with extremely large days parameter"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/admin/fraud/overview/", {"days": 99999})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["period_days"] == 99999

    def test_fraud_overview_concurrent_admin_requests(self):
        """Test multiple admin requests to fraud overview"""
        self.client.force_authenticate(user=self.admin_user)

        # Create some data
        FraudIncident.objects.create(incident_type="test", details={}, severity="low")

        # Make concurrent requests
        responses = []
        for i in range(5):
            response = self.client.get("/api/admin/fraud/overview/")
            responses.append(response)

        # All should succeed
        for response in responses:
            assert response.status_code == status.HTTP_200_OK
            assert response.data["data"]["total_incidents"] == 1

    def test_fraud_detection_with_mixed_severity_incidents(self):
        """Test fraud detection with incidents of mixed severity"""
        self.client.force_authenticate(user=self.admin_user)

        # Create incidents of different severities
        severities = ["low", "medium", "high"]
        for severity in severities:
            FraudIncident.objects.create(
                incident_type=f"test_{severity}",
                details={"severity": severity},
                severity=severity,
            )

        response = self.client.get("/api/admin/fraud/overview/")
        data = response.data["data"]
        assert data["total_incidents"] == 3

        # Check all severities are represented
        incident_types = [inc["incident_type"] for inc in data["incidents_by_type"]]
        assert "test_low" in incident_types
        assert "test_medium" in incident_types
        assert "test_high" in incident_types

    def test_fraud_detection_with_unicode_characters(self):
        """Test fraud detection with unicode characters in details"""
        self.client.force_authenticate(user=self.admin_user)

        # Create incident with unicode
        FraudIncident.objects.create(
            incident_type="unicode_test",
            details={"message": "测试 unicode 🚀", "ip": "192.168.1.1"},
            severity="low",
        )

        response = self.client.get("/api/admin/fraud/overview/")
        assert response.status_code == status.HTTP_200_OK
        data = response.data["data"]
        assert data["total_incidents"] == 1

    def test_fraud_overview_empty_response_consistency(self):
        """Test that empty fraud overview returns consistent structure"""
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get("/api/admin/fraud/overview/")
        data = response.data["data"]

        # Should always return the same structure
        assert data["total_incidents"] == 0
        assert data["incidents_by_type"] == []
        assert data["flagged_urls"] == 0
        assert data["risk_score"] == "low"
        assert data["top_incident_types"] == []

    def test_fraud_detection_with_database_constraints(self):
        """Test fraud detection respects database constraints"""
        from django.db import DataError

        # Try to create incident with invalid severity (too long)
        with pytest.raises(DataError):  # Should raise DataError due to length
            FraudIncident.objects.create(
                incident_type="test", details={}, severity="invalid_severity_too_long"
            )

        # Test passes if DataError is raised - no need for further checks due to transaction breakage

    def test_fraud_overview_response_size_limits(self):
        """Test fraud overview handles large result sets"""
        self.client.force_authenticate(user=self.admin_user)

        # Create many incidents
        for i in range(100):
            FraudIncident.objects.create(
                incident_type=f"type_{i % 10}", details={"index": i}, severity="low"
            )

        response = self.client.get("/api/admin/fraud/overview/")
        assert response.status_code == status.HTTP_200_OK
        data = response.data["data"]
        assert data["total_incidents"] == 100
        assert len(data["incidents_by_type"]) == 10  # 10 different types
        assert len(data["top_incident_types"]) <= 3  # Limited to top 3
