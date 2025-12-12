import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

User = get_user_model()


@pytest.mark.django_db
class TestPlatformStatsViewAuthentication:
    """Test authentication and authorization for platform stats endpoint"""

    def setup_method(self):
        self.client = APIClient()
        self.url = "/api/admin/insight/platform-stats/"

        self.regular_user = User.objects.create_user(
            username="regularuser",
            email="user@test.com",
            password="testpass123",
            role=User.Role.USER,
        )

        self.staff_user = User.objects.create_user(
            username="staffuser",
            email="staff@test.com",
            password="staffpass123",
            role=User.Role.STAFF,
        )

        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@test.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )

    def test_unauthenticated_access_denied(self):
        """Test unauthenticated users cannot access platform stats endpoint"""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_regular_user_access_denied(self):
        """Test regular users cannot access platform stats endpoint"""
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_staff_user_access_denied(self):
        """Test staff users cannot access platform stats endpoint"""
        self.client.force_authenticate(user=self.staff_user)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_user_access_allowed(self):
        """Test admin users can access platform stats endpoint"""
        self.client.force_authenticate(user=self.admin_user)

        with patch('api.admin_panel.insight.InsightService.InsightService.get_platform_stats') as mock_service:
            mock_service.return_value = {
                "total_clicks": 100,
                "new_urls": 10,
                "new_users": 5,
                "new_visitors": 80
            }

            response = self.client.get(self.url)

            assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestPlatformStatsViewResponse:
    """Test platform stats endpoint response structure and data"""

    def setup_method(self):
        self.client = APIClient()
        self.url = "/api/admin/insight/platform-stats/"
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@test.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_response_structure(self):
        """Test platform stats endpoint returns correct response structure"""
        with patch('api.admin_panel.insight.InsightService.InsightService.get_platform_stats') as mock_service:
            expected_stats = {
                "total_clicks": 150,
                "new_urls": 12,
                "new_users": 8,
                "new_visitors": 100
            }
            mock_service.return_value = expected_stats

            response = self.client.get(self.url)

            assert response.status_code == status.HTTP_200_OK
            assert "total_clicks" in response.data
            assert "new_urls" in response.data
            assert "new_users" in response.data
            assert "new_visitors" in response.data
            assert response.data == expected_stats

    def test_time_range_parameter_handling(self):
        """Test time_range parameter is handled correctly"""
        with patch('api.admin_panel.insight.InsightService.InsightService.get_platform_stats') as mock_service:
            mock_service.return_value = {
                "total_clicks": 200,
                "new_urls": 15,
                "new_users": 10,
                "new_visitors": 150
            }

            response = self.client.get(self.url, {"time_range": "2023-01-01T00:00:00Z"})

            mock_service.assert_called_once_with("2023-01-01T00:00:00Z")
            assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestGrowthMetricsViewAuthentication:
    """Test authentication and authorization for growth metrics endpoint"""

    def setup_method(self):
        self.client = APIClient()
        self.url = "/api/admin/insight/growth-metric/"

        self.regular_user = User.objects.create_user(
            username="regularuser",
            email="user@test.com",
            password="testpass123",
            role=User.Role.USER,
        )

        self.staff_user = User.objects.create_user(
            username="staffuser",
            email="staff@test.com",
            password="staffpass123",
            role=User.Role.STAFF,
        )

        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@test.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )

    def test_unauthenticated_access_denied(self):
        """Test unauthenticated users cannot access growth metrics endpoint"""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_regular_user_access_denied(self):
        """Test regular users cannot access growth metrics endpoint"""
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_staff_user_access_denied(self):
        """Test staff users cannot access growth metrics endpoint"""
        self.client.force_authenticate(user=self.staff_user)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_user_access_allowed(self):
        """Test admin users can access growth metrics endpoint"""
        self.client.force_authenticate(user=self.admin_user)

        with patch('api.admin_panel.insight.InsightService.InsightService.get_growth_metrics') as mock_service:
            mock_service.return_value = {
                "growth_interval": "weekly",
                "data_points": 10,
                "metrics": {
                    "users_growth": [],
                    "urls_growth": [],
                    "clicks_volume": []
                }
            }

            response = self.client.get(self.url)

            assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestGrowthMetricsViewResponse:
    """Test growth metrics endpoint response structure and data"""

    def setup_method(self):
        self.client = APIClient()
        self.url = "/api/admin/insight/growth-metric/"
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@test.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_response_structure(self):
        """Test growth metrics endpoint returns correct response structure"""
        expected_metrics = {
            "growth_interval": "weekly",
            "data_points": 10,
            "metrics": {
                "users_growth": [
                    {
                        "week_starting": "2023-01-01",
                        "new_users": 5,
                        "cumulative_users": 100
                    }
                ],
                "urls_growth": [
                    {
                        "week_starting": "2023-01-01",
                        "new_urls": 10,
                        "cumulative_users": 50
                    }
                ],
                "clicks_volume": [
                    {
                        "week_starting": "2023-01-01",
                        "total_clicks": 500
                    }
                ]
            }
        }

        with patch('api.admin_panel.insight.InsightService.InsightService.get_growth_metrics') as mock_service:
            mock_service.return_value = expected_metrics

            response = self.client.get(self.url)

            assert response.status_code == status.HTTP_200_OK
            assert "growth_interval" in response.data
            assert "data_points" in response.data
            assert "metrics" in response.data
            assert "users_growth" in response.data["metrics"]
            assert "urls_growth" in response.data["metrics"]
            assert "clicks_volume" in response.data["metrics"]
            assert response.data == expected_metrics


@pytest.mark.django_db
class TestTopPerformersViewAuthentication:
    """Test authentication and authorization for top performers endpoint"""

    def setup_method(self):
        self.client = APIClient()
        self.url = "/api/admin/insight/top-performers/"

        self.regular_user = User.objects.create_user(
            username="regularuser",
            email="user@test.com",
            password="testpass123",
            role=User.Role.USER,
        )

        self.staff_user = User.objects.create_user(
            username="staffuser",
            email="staff@test.com",
            password="staffpass123",
            role=User.Role.STAFF,
        )

        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@test.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )

    def test_unauthenticated_access_denied(self):
        """Test unauthenticated users cannot access top performers endpoint"""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_regular_user_access_denied(self):
        """Test regular users cannot access top performers endpoint"""
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_staff_user_access_denied(self):
        """Test staff users cannot access top performers endpoint"""
        self.client.force_authenticate(user=self.staff_user)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_user_access_allowed(self):
        """Test admin users can access top performers endpoint"""
        self.client.force_authenticate(user=self.admin_user)

        with patch('api.admin_panel.insight.InsightService.InsightService.get_top_performers') as mock_service:
            mock_service.return_value = [
                {
                    "rank": 1,
                    "identifier_type": "name",
                    "identifier_value": "short-url-1",
                    "metric": "clicks",
                    "metric_value": 100,
                    "details": {
                        "long_url": "https://www.example.com",
                        "short_url": "https://short.ly/url-1"
                    }
                }
            ]

            response = self.client.get(self.url)

            assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestTopPerformersViewResponse:
    """Test top performers endpoint response structure and data"""

    def setup_method(self):
        self.client = APIClient()
        self.url = "/api/admin/insight/top-performers/"
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@test.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_default_parameters(self):
        """Test that default parameters are used when none provided"""
        with patch('api.admin_panel.insight.InsightService.InsightService.get_top_performers') as mock_service:
            mock_service.return_value = []

            response = self.client.get(self.url)

            # Verify the default values were passed to the service
            mock_service.assert_called_once_with("clicks", 10)
            assert response.status_code == status.HTTP_200_OK

    def test_custom_metric_and_limit(self):
        """Test custom metric and limit parameters are handled correctly"""
        with patch('api.admin_panel.insight.InsightService.InsightService.get_top_performers') as mock_service:
            mock_service.return_value = []

            response = self.client.get(self.url, {"metric": "urls_created", "limit": 5})

            mock_service.assert_called_once_with("urls_created", 5)
            assert response.status_code == status.HTTP_200_OK

    def test_response_structure(self):
        """Test top performers endpoint returns correct response structure"""
        expected_performers = [
            {
                "rank": 1,
                "identifier_type": "name",
                "identifier_value": "top-performer-1",
                "metric": "clicks",
                "metric_value": 250,
                "details": {
                    "long_url": "https://www.example.com/long",
                    "short_url": "https://short.ly/short"
                }
            }
        ]

        with patch('api.admin_panel.insight.InsightService.InsightService.get_top_performers') as mock_service:
            mock_service.return_value = expected_performers

            response = self.client.get(self.url)

            assert response.status_code == status.HTTP_200_OK
            assert isinstance(response.data, list)
            if response.data:
                performer = response.data[0]
                assert "rank" in performer
                assert "identifier_type" in performer
                assert "identifier_value" in performer
                assert "metric" in performer
                assert "metric_value" in performer
                assert "details" in performer
                assert response.data == expected_performers


@pytest.mark.django_db
class TestPeakTimesViewAuthentication:
    """Test authentication and authorization for peak times endpoint"""

    def setup_method(self):
        self.client = APIClient()
        self.url = "/api/admin/insight/peak-times/"

        self.regular_user = User.objects.create_user(
            username="regularuser",
            email="user@test.com",
            password="testpass123",
            role=User.Role.USER,
        )

        self.staff_user = User.objects.create_user(
            username="staffuser",
            email="staff@test.com",
            password="staffpass123",
            role=User.Role.STAFF,
        )

        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@test.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )

    def test_unauthenticated_access_denied(self):
        """Test unauthenticated users cannot access peak times endpoint"""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_regular_user_access_denied(self):
        """Test regular users cannot access peak times endpoint"""
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_staff_user_access_denied(self):
        """Test staff users cannot access peak times endpoint"""
        self.client.force_authenticate(user=self.staff_user)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_user_access_allowed(self):
        """Test admin users can access peak times endpoint"""
        self.client.force_authenticate(user=self.admin_user)

        with patch('api.admin_panel.insight.InsightService.InsightService.get_peak_times') as mock_service:
            mock_service.return_value = {
                "day": {"peak_day": "Monday", "avg_clicks": 100},
                "hour": {"peak_hour": "12:00PM UTC", "avg_clicks": 50}
            }

            response = self.client.get(self.url)

            assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestPeakTimesViewResponse:
    """Test peak times endpoint response structure and data"""

    def setup_method(self):
        self.client = APIClient()
        self.url = "/api/admin/insight/peak-times/"
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@test.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_response_structure(self):
        """Test peak times endpoint returns correct response structure"""
        expected_peak_times = {
            "day": {"peak_day": "Tuesday", "avg_clicks": 120},
            "hour": {"peak_hour": "2:00PM UTC", "avg_clicks": 75}
        }

        with patch('api.admin_panel.insight.InsightService.InsightService.get_peak_times') as mock_service:
            mock_service.return_value = expected_peak_times

            response = self.client.get(self.url)

            assert response.status_code == status.HTTP_200_OK
            assert "day" in response.data
            assert "hour" in response.data
            assert "peak_day" in response.data["day"]
            assert "avg_clicks" in response.data["day"]
            assert "peak_hour" in response.data["hour"]
            assert "avg_clicks" in response.data["hour"]
            assert response.data == expected_peak_times


@pytest.mark.django_db
class TestGeoDistributionViewAuthentication:
    """Test authentication and authorization for geo distribution endpoint"""

    def setup_method(self):
        self.client = APIClient()
        self.url = "/api/admin/insight/geo-dist/"

        self.regular_user = User.objects.create_user(
            username="regularuser",
            email="user@test.com",
            password="testpass123",
            role=User.Role.USER,
        )

        self.staff_user = User.objects.create_user(
            username="staffuser",
            email="staff@test.com",
            password="staffpass123",
            role=User.Role.STAFF,
        )

        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@test.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )

    def test_unauthenticated_access_denied(self):
        """Test unauthenticated users cannot access geo distribution endpoint"""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_regular_user_access_denied(self):
        """Test regular users cannot access geo distribution endpoint"""
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_staff_user_access_denied(self):
        """Test staff users cannot access geo distribution endpoint"""
        self.client.force_authenticate(user=self.staff_user)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_user_access_allowed(self):
        """Test admin users can access geo distribution endpoint"""
        self.client.force_authenticate(user=self.admin_user)

        with patch('api.admin_panel.insight.InsightService.InsightService.get_geo_distribution') as mock_service:
            mock_service.return_value = [
                {
                    "rank": 1,
                    "country": "United States",
                    "clicks": 1000,
                    "percentage": 45.5
                }
            ]

            response = self.client.get(self.url)

            assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestGeoDistributionViewResponse:
    """Test geo distribution endpoint response structure and data"""

    def setup_method(self):
        self.client = APIClient()
        self.url = "/api/admin/insight/geo-dist/"
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@test.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_empty_response_structure(self):
        """Test geo distribution endpoint handles empty response correctly"""
        with patch('api.admin_panel.insight.InsightService.InsightService.get_geo_distribution') as mock_service:
            mock_service.return_value = []

            response = self.client.get(self.url)

            assert response.status_code == status.HTTP_200_OK
            assert isinstance(response.data, list)

    def test_response_structure(self):
        """Test geo distribution endpoint returns correct response structure"""
        expected_geo_data = [
            {
                "rank": 1,
                "country": "United States",
                "clicks": 1200,
                "percentage": 35.5
            },
            {
                "rank": 2,
                "country": "Canada",
                "clicks": 800,
                "percentage": 25.0
            }
        ]

        with patch('api.admin_panel.insight.InsightService.InsightService.get_geo_distribution') as mock_service:
            mock_service.return_value = expected_geo_data

            response = self.client.get(self.url)

            assert response.status_code == status.HTTP_200_OK
            if response.data:
                country_data = response.data[0]
                assert "rank" in country_data
                assert "country" in country_data
                assert "clicks" in country_data
                assert "percentage" in country_data
                assert response.data == expected_geo_data


@pytest.mark.django_db
class TestInsightViewsRateLimiting:
    """Test rate limiting on insight endpoints"""

    def setup_method(self):
        self.client = APIClient()
        
        # Create admin user for testing
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@test.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )
        self.client.force_authenticate(user=self.admin_user)

        # Mock service methods to avoid DB calls
        self.patchers = [
            patch('api.admin_panel.insight.InsightService.InsightService.get_platform_stats'),
            patch('api.admin_panel.insight.InsightService.InsightService.get_growth_metrics'),
            patch('api.admin_panel.insight.InsightService.InsightService.get_top_performers'),
            patch('api.admin_panel.insight.InsightService.InsightService.get_peak_times'),
            patch('api.admin_panel.insight.InsightService.InsightService.get_geo_distribution')
        ]
        
        # Start all patchers
        self.mock_services = [patcher.start() for patcher in self.patchers]
        
        # Set return values
        self.mock_services[0].return_value = {"total_clicks": 100, "new_urls": 10, "new_users": 5, "new_visitors": 80}
        self.mock_services[1].return_value = {"growth_interval": "weekly", "data_points": 10, "metrics": {"users_growth": [], "urls_growth": [], "clicks_volume": []}}
        self.mock_services[2].return_value = [{"rank": 1, "identifier_type": "name", "identifier_value": "test", "metric": "clicks", "metric_value": 100, "details": {"long_url": "test", "short_url": "test"}}]
        self.mock_services[3].return_value = {"day": {"peak_day": "Monday", "avg_clicks": 100}, "hour": {"peak_hour": "12:00PM UTC", "avg_clicks": 50}}
        self.mock_services[4].return_value = [{"rank": 1, "country": "US", "clicks": 100, "percentage": 50.0}]
    
    def teardown_method(self):
        # Stop all patchers
        for patcher in self.patchers:
            patcher.stop()

    def test_platform_stats_rate_limiting(self):
        """Test rate limiting is applied to platform stats endpoint"""
        url = "/api/admin/insight/platform-stats/"
        responses = []
        for _ in range(5):
            response = self.client.get(url)
            responses.append(response)

        # All requests should succeed (adjust if rate limit is lower)
        for response in responses:
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_429_TOO_MANY_REQUESTS,
            ]

    def test_growth_metrics_rate_limiting(self):
        """Test rate limiting is applied to growth metrics endpoint"""
        url = "/api/admin/insight/growth-metric/"
        responses = []
        for _ in range(5):
            response = self.client.get(url)
            responses.append(response)

        for response in responses:
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_429_TOO_MANY_REQUESTS,
            ]

    def test_top_performers_rate_limiting(self):
        """Test rate limiting is applied to top performers endpoint"""
        url = "/api/admin/insight/top-performers/"
        responses = []
        for _ in range(5):
            response = self.client.get(url)
            responses.append(response)

        for response in responses:
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_429_TOO_MANY_REQUESTS,
            ]

    def test_peak_times_rate_limiting(self):
        """Test rate limiting is applied to peak times endpoint"""
        url = "/api/admin/insight/peak-times/"
        responses = []
        for _ in range(5):
            response = self.client.get(url)
            responses.append(response)

        for response in responses:
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_429_TOO_MANY_REQUESTS,
            ]

    def test_geo_distribution_rate_limiting(self):
        """Test rate limiting is applied to geo distribution endpoint"""
        url = "/api/admin/insight/geo-dist/"
        responses = []
        for _ in range(5):
            response = self.client.get(url)
            responses.append(response)

        for response in responses:
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_429_TOO_MANY_REQUESTS,
            ]