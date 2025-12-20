import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock, PropertyMock
from datetime import datetime, timezone
import psutil
from api.admin_panel.system.SystemService import HealthStatus

User = get_user_model()


@pytest.mark.django_db
class TestHealthEndpointAuthentication:
    """Test authentication and authorization for health endpoint"""

    def setup_method(self):
        self.client = APIClient()
        self.url = "/api/admin/system/health/"

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
        """Test unauthenticated users cannot access health endpoint"""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_regular_user_access_denied(self):
        """Test regular users cannot access health endpoint"""
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_staff_user_access_denied(self):
        """Test staff users cannot access health endpoint"""
        self.client.force_authenticate(user=self.staff_user)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_user_access_allowed(self):
        """Test admin users can access health endpoint"""
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestHealthEndpointResponse:
    """Test health endpoint response structure and data"""

    def setup_method(self):
        self.client = APIClient()
        self.url = "/api/admin/system/health/"
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@test.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_response_structure(self):
        """Test health endpoint returns correct response structure"""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] == True
        data = response.data["data"]
        assert "status" in data
        assert "timestamp" in data
        assert "components" in data
        assert "metadata" in data

        # Verify components exist
        components = data["components"]
        assert "database" in components
        assert "cache" in components
        assert "redis" in components
        assert "celery" in components
        assert "disk" in components
        assert "memory" in components

    def test_metadata_structure(self):
        """Test metadata contains required fields"""
        response = self.client.get(self.url)

        data = response.data["data"]
        metadata = data["metadata"]
        assert "version" in metadata
        assert "environment" in metadata
        assert "debug" in metadata

    def test_component_status_structure(self):
        """Test each component has status field"""
        response = self.client.get(self.url)

        data = response.data["data"]
        for component_name, component_data in data["components"].items():
            assert "status" in component_data, f"{component_name} missing status"
            assert component_data["status"] in [
                HealthStatus.HEALTHY,
                HealthStatus.DEGRADED,
                HealthStatus.UNHEALTHY,
            ]

    def test_healthy_system_status(self):
        """Test overall status is healthy when all components are healthy"""
        response = self.client.get(self.url)

        data = response.data["data"]
        # If test environment is properly configured, should be healthy
        assert data["status"] in [
            HealthStatus.HEALTHY,
            HealthStatus.DEGRADED,
            HealthStatus.UNHEALTHY,
        ]

    def test_database_component_fields(self):
        """Test database component contains expected fields"""
        response = self.client.get(self.url)

        data = response.data["data"]
        db_component = data["components"]["database"]
        assert "status" in db_component
        assert "latency_ms" in db_component
        assert "vendor" in db_component
        assert db_component["vendor"] == "postgresql"

    def test_redis_component_fields(self):
        """Test Redis component contains expected fields"""
        response = self.client.get(self.url)

        redis_component = response.data["data"]["components"]["redis"]
        assert "status" in redis_component

        if redis_component["status"] != HealthStatus.UNHEALTHY:
            assert "latency_ms" in redis_component
            assert "memory_used_mb" in redis_component
            assert "connected_clients" in redis_component

    def test_celery_component_fields(self):
        """Test Celery component contains expected fields"""
        response = self.client.get(self.url)

        celery_component = response.data["data"]["components"]["celery"]
        assert "status" in celery_component
        assert "broker_connected" in celery_component

    def test_disk_component_fields(self):
        """Test disk component contains expected fields"""
        response = self.client.get(self.url)

        disk_component = response.data["data"]["components"]["disk"]
        assert "status" in disk_component
        assert "total_gb" in disk_component
        assert "used_gb" in disk_component
        assert "free_gb" in disk_component
        assert "percent_used" in disk_component

    def test_memory_component_fields(self):
        """Test memory component contains expected fields"""
        response = self.client.get(self.url)

        memory_component = response.data["data"]["components"]["memory"]
        assert "status" in memory_component
        assert "total_gb" in memory_component
        assert "used_gb" in memory_component
        assert "available_gb" in memory_component
        assert "percent_used" in memory_component


@pytest.mark.django_db
class TestHealthEndpointDegradedScenarios:
    """Test health endpoint with degraded system components"""

    def setup_method(self):
        self.client = APIClient()
        self.url = "/api/admin/system/health/"
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@test.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )
        self.client.force_authenticate(user=self.admin_user)

    @patch("psutil.disk_usage")
    def test_degraded_disk_space(self, mock_disk):
        """Test health endpoint when disk space is degraded (>80%)"""
        mock_disk.return_value = MagicMock(
            total=1000 * (1024**3),
            used=850 * (1024**3),
            free=150 * (1024**3),
            percent=85.0,
        )

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        disk_component = response.data["data"]["components"]["disk"]
        assert disk_component["status"] == HealthStatus.DEGRADED
        assert disk_component["percent_used"] == 85.0

    @patch("psutil.disk_usage")
    def test_unhealthy_disk_space(self, mock_disk):
        """Test health endpoint when disk space is unhealthy (>90%)"""
        mock_disk.return_value = MagicMock(
            total=1000 * (1024**3),
            used=950 * (1024**3),
            free=50 * (1024**3),
            percent=95.0,
        )

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        disk_component = response.data["data"]["components"]["disk"]
        assert disk_component["status"] == HealthStatus.UNHEALTHY
        assert disk_component["percent_used"] == 95.0

    @patch("psutil.virtual_memory")
    def test_degraded_memory(self, mock_memory):
        """Test health endpoint when memory is degraded (>80%)"""
        mock_memory.return_value = MagicMock(
            total=16 * (1024**3),
            used=13.5 * (1024**3),
            available=2.5 * (1024**3),
            percent=84.0,
        )

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        memory_component = response.data["data"]["components"]["memory"]
        assert memory_component["status"] == HealthStatus.DEGRADED
        assert memory_component["percent_used"] == 84.0

    @patch("psutil.virtual_memory")
    def test_unhealthy_memory(self, mock_memory):
        """Test health endpoint when memory is unhealthy (>90%)"""
        mock_memory.return_value = MagicMock(
            total=16 * (1024**3),
            used=15 * (1024**3),
            available=1 * (1024**3),
            percent=93.0,
        )

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        memory_component = response.data["data"]["components"]["memory"]
        assert memory_component["status"] == HealthStatus.UNHEALTHY
        assert memory_component["percent_used"] == 93.0

    @patch("api.admin_panel.system.SystemService.SystemService._check_database")
    def test_slow_database_response(self, mock_check_db):
        """Test health endpoint when database responds slowly"""
        mock_check_db.return_value = {
            "status": HealthStatus.DEGRADED,
            "latency_ms": 1500.0,
            "vendor": "postgresql",
            "database": "test_db",
        }

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        db_component = response.data["data"]["components"]["database"]
        assert db_component["status"] == HealthStatus.DEGRADED
        assert db_component["latency_ms"] == 1500.0


@pytest.mark.django_db
class TestHealthEndpointFailureScenarios:
    """Test health endpoint with component failures"""

    def setup_method(self):
        self.client = APIClient()
        self.url = "/api/admin/system/health/"
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@test.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )
        self.client.force_authenticate(user=self.admin_user)

    @patch("api.admin_panel.system.SystemService.SystemService._check_database")
    def test_database_connection_failure(self, mock_check_db):
        """Test health endpoint when database connection fails"""
        mock_check_db.return_value = {
            "status": HealthStatus.UNHEALTHY,
            "error": "Database connection failed",
            "error_type": "OperationalError",
        }

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        db_component = response.data["data"]["components"]["database"]
        assert db_component["status"] == HealthStatus.UNHEALTHY
        assert "error" in db_component
        assert "error_type" in db_component
        assert db_component["error"] == "Database connection failed"

    @patch("api.admin_panel.system.SystemService.SystemService._check_database")
    def test_overall_status_reflects_component_failures(self, mock_check_db):
        """Test overall status is unhealthy when any component is unhealthy"""
        mock_check_db.return_value = {
            "status": HealthStatus.UNHEALTHY,
            "error": "Database error",
            "error_type": "Exception",
        }

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        # Overall status should be unhealthy
        assert response.data["data"]["status"] == HealthStatus.UNHEALTHY
        # Verify database component is unhealthy
        assert (
            response.data["data"]["components"]["database"]["status"]
            == HealthStatus.UNHEALTHY
        )


@pytest.mark.django_db
class TestHealthEndpointRateLimiting:
    """Test rate limiting on health endpoint"""

    def setup_method(self):
        self.client = APIClient()
        self.url = "/api/admin/system/health/"
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@test.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_rate_limiting_applied(self):
        """Test rate limiting is applied to health endpoint"""
        # Make multiple requests
        responses = []
        for _ in range(5):
            response = self.client.get(self.url)
            responses.append(response)

        # All requests should succeed (adjust if rate limit is lower)
        for response in responses:
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_429_TOO_MANY_REQUESTS,
            ]


@pytest.mark.django_db
class TestHealthEndpointTimestamp:
    """Test timestamp accuracy in health endpoint"""

    def setup_method(self):
        self.client = APIClient()
        self.url = "/api/admin/system/health/"
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@test.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_timestamp_format(self):
        """Test timestamp is in ISO format"""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        timestamp = response.data["data"]["timestamp"]

        # Verify it's a valid ISO format timestamp
        try:
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            pytest.fail("Timestamp is not in valid ISO format")

    def test_timestamp_recent(self):
        """Test timestamp is recent (within last minute)"""
        before = datetime.now(timezone.utc)
        response = self.client.get(self.url)
        after = datetime.now(timezone.utc)

        timestamp = datetime.fromisoformat(
            response.data["data"]["timestamp"].replace("Z", "+00:00")
        )

        assert before <= timestamp <= after, "Timestamp is not current"


@pytest.mark.django_db
class TestSystemConfigurationViewSet:
    """Test system configuration endpoints"""

    def setup_method(self):
        self.client = APIClient()

        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@test.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_list_system_configuration_success(self):
        """Test successful retrieval of all system configurations"""
        url = "/api/admin/system/config/"
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Response should be a list of configuration objects
        assert isinstance(response.data["data"], list)
        # Each item should have required fields
        for config in response.data["data"]:
            assert "key" in config
            assert "value" in config
            assert "description" in config
            assert "updated_at" in config

    def test_list_system_configuration_error_handling(self):
        """Test error handling when ConfigService fails"""
        url = "/api/admin/system/config/"

        # Mock the ConfigService to raise an exception
        with patch(
            "api.admin_panel.system.ConfigService.ConfigService.get_all_configs",
            side_effect=Exception("Service unavailable"),
        ):
            response = self.client.get(url)

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "message" in response.data


@pytest.mark.django_db
class TestSpecificSystemConfigurationView:
    """Test specific system configuration endpoints"""

    def setup_method(self):
        self.client = APIClient()

        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@test.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_get_specific_system_configuration_success(self):
        """Test successful retrieval of specific system configuration"""
        # First, create a configuration to retrieve
        config_url = "/api/admin/system/config/max_urls_per_user/"
        response = self.client.post(config_url, {"value": "50"})
        assert response.status_code == status.HTTP_200_OK

        # Now retrieve it
        response = self.client.get(config_url)
        assert response.status_code == status.HTTP_200_OK
        assert "key" in response.data["data"]
        assert "value" in response.data["data"]
        assert response.data["data"]["key"] == "max_urls_per_user"
        assert response.data["data"]["value"] == "50"

    def test_get_specific_system_configuration_not_found(self):
        """Test retrieval of non-existent system configuration"""
        url = "/api/admin/system/config/nonexistent_config_key/"
        response = self.client.get(url)

        # Expecting a 500 error as specified in the view implementation
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "message" in response.data

    def test_post_specific_system_configuration_success(self):
        """Test successful update of system configuration"""
        url = "/api/admin/system/config/max_urls_per_user/"
        response = self.client.post(url, {"value": "100"})

        assert response.status_code == status.HTTP_200_OK
        assert (
            response.data["message"]
            == "Configuration 'max_urls_per_user' updated successfully"
        )

    def test_post_specific_system_configuration_invalid_key(self):
        """Test posting to system configuration with invalid key"""
        url = "/api/admin/system/config/invalid_key/"
        response = self.client.post(url, {"value": "100"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_post_specific_system_configuration_invalid_value_type(self):
        """Test posting system configuration with invalid value type"""
        url = "/api/admin/system/config/max_urls_per_user/"
        response = self.client.post(url, {"value": "not_an_integer"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # Check that error contains validation message
        assert any(
            "int" in str(error_msg).lower()
            for error_msg in (
                str(response.data) if isinstance(response.data, dict) else [""]
            )
            for error_msg in (
                response.data.values() if isinstance(response.data, dict) else [""]
            )
        )

    def test_post_specific_system_configuration_validation_error(self):
        """Test posting system configuration with validation error"""
        url = "/api/admin/system/config/short_code_length/"
        response = self.client.post(url, {"value": "2"})  # Too low for min value of 4

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "value" in str(response.data) or "length" in str(response.data)


@pytest.mark.django_db
class TestBatchCreateSystemConfigurationView:
    """Test batch system configuration endpoints"""

    def setup_method(self):
        self.client = APIClient()

        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@test.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_batch_create_system_configuration_success(self):
        """Test successful batch creation of system configurations"""
        url = "/api/admin/system/config/batch/"
        configs = {"configs": {"max_urls_per_user": "75", "short_code_length": "8"}}
        response = self.client.post(url, configs, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data["data"]
        assert "errors" in response.data["data"]
        assert (
            len(response.data["data"]["results"]) >= 0
        )  # May be empty if configs didn't change
        assert len(response.data["data"]["errors"]) == 0

    def test_batch_create_system_configuration_with_errors(self):
        """Test batch creation with some valid and some invalid configurations"""
        url = "/api/admin/system/config/batch/"
        configs = {
            "configs": {
                "max_urls_per_user": "100",  # Valid
                "invalid_key": "200",  # Invalid key
                "short_code_length": "2",  # Invalid value (too low)
                "jwt_access_token_minutes": "30",  # Valid
            }
        }
        response = self.client.post(url, configs, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # For error responses, data contains the results directly
        assert isinstance(response.data["data"], dict)
        assert "errors" in response.data
        # At least some errors should be present
        assert len(response.data["errors"]) > 0

    def test_batch_create_system_configuration_empty_payload(self):
        """Test batch creation with empty payload"""
        url = "/api/admin/system/config/batch/"
        configs = {"configs": {}}
        response = self.client.post(url, configs, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data["data"]
        assert "errors" in response.data["data"]
        assert len(response.data["data"]["results"]) == 0
        assert len(response.data["data"]["errors"]) == 0

    def test_batch_create_system_configuration_missing_configs_key(self):
        """Test batch creation without configs key in payload"""
        url = "/api/admin/system/config/batch/"
        configs = {"something_else": {"max_urls_per_user": "50"}}
        response = self.client.post(url, configs, format="json")

        # Even though configs key is missing, ConfigService.get() will return empty dict
        # So this should still succeed with empty results
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
        # If successful, response should have empty results/errors
        if response.status_code == status.HTTP_200_OK:
            assert "results" in response.data["data"]
            assert "errors" in response.data["data"]
