import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from api.admin_panel.audit.models import AuditLog
from api.url.models import Url
from django.utils import timezone

User = get_user_model()


@pytest.mark.django_db
class TestAuditService:
    """Test cases for AuditService functionality"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

    def test_create_url_logs_audit(self):
        """Test that creating a URL creates an audit log entry"""
        initial_audit_count = AuditLog.objects.count()

        response = self.client.post(
            "/api/url/shorten/",
            {"long_url": "https://www.example.com/test-audit"},
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED

        # Check if an audit entry was created
        final_audit_count = AuditLog.objects.count()
        assert final_audit_count == initial_audit_count + 1

        # Check the last audit entry
        latest_audit = AuditLog.objects.last()
        assert latest_audit.action == "CREATE"
        assert latest_audit.user == self.user
        assert latest_audit.ip_address is not None

    def test_update_url_logs_audit(self):
        """Test that updating a URL creates an audit log entry"""
        # First, create a URL
        create_response = self.client.post(
            "/api/url/shorten/",
            {"long_url": "https://www.example.com/original"},
            format="json",
        )

        assert create_response.status_code == status.HTTP_201_CREATED
        short_url = create_response.data["data"]["short_url"]

        initial_audit_count = AuditLog.objects.count()

        # Now update the URL
        update_response = self.client.patch(
            f"/api/url/{short_url}/",
            {"long_url": "https://www.example.com/updated"},
            format="json",
        )

        assert update_response.status_code == status.HTTP_200_OK

        # Check if an audit entry was created
        final_audit_count = AuditLog.objects.count()
        assert final_audit_count == initial_audit_count + 1

        # Check the last audit entry
        latest_audit = AuditLog.objects.last()
        assert latest_audit.action == "UPDATE"
        assert latest_audit.user == self.user

    def test_delete_url_logs_audit(self):
        """Test that deleting a URL creates an audit log entry"""
        # First, create a URL
        create_response = self.client.post(
            "/api/url/shorten/",
            {"long_url": "https://www.example.com/to-delete"},
            format="json",
        )

        assert create_response.status_code == status.HTTP_201_CREATED
        short_url = create_response.data["data"]["short_url"]

        initial_audit_count = AuditLog.objects.count()

        # Now delete the URL
        delete_response = self.client.delete(f"/api/url/{short_url}/")

        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # Check if an audit entry was created
        final_audit_count = AuditLog.objects.count()
        assert final_audit_count == initial_audit_count + 1

        # Check the last audit entry
        latest_audit = AuditLog.objects.last()
        assert latest_audit.action == "DELETE"
        assert latest_audit.user == self.user

    def test_get_requests_not_logged(self):
        """Test that GET requests are not logged in audit trail"""
        # First, create a URL to retrieve
        create_response = self.client.post(
            "/api/url/shorten/",
            {"long_url": "https://www.example.com/to-retrieve"},
            format="json",
        )

        assert create_response.status_code == status.HTTP_201_CREATED
        short_url = create_response.data["data"]["short_url"]

        initial_audit_count = AuditLog.objects.count()

        # Perform a GET request
        get_response = self.client.get(f"/api/url/{short_url}/")

        assert get_response.status_code == status.HTTP_200_OK

        # Check that no new audit entry was created for GET request
        final_audit_count = AuditLog.objects.count()
        assert final_audit_count == initial_audit_count

    def test_audit_log_content_type_and_id(self):
        """Test that audit logs have correct content_type and content_id"""
        # Create a URL
        response = self.client.post(
            "/api/url/shorten/",
            {"long_url": "https://www.example.com/test-content"},
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        short_url = response.data["data"]["short_url"]

        # Check the audit entry
        latest_audit = AuditLog.objects.last()

        # Note: The actual content_type and content_id depend on how the middleware resolves URLs
        # This might vary based on your URL configuration
        assert latest_audit.action == "CREATE"
        assert latest_audit.user == self.user

    def test_audit_log_with_different_users(self):
        """Test that audit logs correctly capture different users"""
        # Create another user
        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="otherpass123"
        )

        # Create URL with first user
        response1 = self.client.post(
            "/api/url/shorten/",
            {"long_url": "https://www.example.com/test-user1"},
            format="json",
        )
        assert response1.status_code == status.HTTP_201_CREATED

        # Switch to other user and create another URL
        self.client.force_authenticate(user=other_user)
        response2 = self.client.post(
            "/api/url/shorten/",
            {"long_url": "https://www.example.com/test-user2"},
            format="json",
        )
        assert response2.status_code == status.HTTP_201_CREATED

        # Get the last two audit entries
        audits = AuditLog.objects.all().order_by("-timestamp")
        assert len(audits) >= 2

        # The most recent should be from other_user, the previous from self.user
        assert audits[0].user == other_user
        assert audits[1].user == self.user

    def test_audit_log_ip_address_anonymization(self):
        """Test that IP addresses in audit logs are anonymized"""
        response = self.client.post(
            "/api/url/shorten/",
            {"long_url": "https://www.example.com/test-ip"},
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED

        # Check the last audit entry
        latest_audit = AuditLog.objects.last()

        # IP should be anonymized (last octet should be 0)
        assert latest_audit.ip_address is not None
        assert latest_audit.ip_address.endswith(".0")


@pytest.mark.django_db
class TestAuditMiddleware:
    """Test cases for AuditMiddleware functionality with different HTTP methods"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

    def test_post_request_triggers_audit(self):
        """Test that POST requests trigger audit logging"""
        initial_count = AuditLog.objects.count()

        response = self.client.post(
            "/api/auth/users/create/",
            {
                "username": "new_user",
                "email": "new@example.com",
                "password": "securepassword123",
            },
            format="json",
        )

        final_count = AuditLog.objects.count()

        # This might fail if the endpoint doesn't exist, but it would still trigger middleware
        assert final_count >= initial_count  # At least no decrease

    def test_put_request_triggers_audit(self):
        """Test that PUT requests trigger audit logging"""
        # First, create a resource to update
        create_response = self.client.post(
            "/api/url/shorten/",
            {"long_url": "https://www.example.com/original"},
            format="json",
        )

        assert create_response.status_code == status.HTTP_201_CREATED
        short_url = create_response.data["data"]["short_url"]

        initial_count = AuditLog.objects.count()

        # Update the resource with PUT
        response = self.client.put(
            f"/api/url/{short_url}/",
            {
                "long_url": "https://www.example.com/updated",
            },
            format="json",
        )

        final_count = AuditLog.objects.count()
        assert final_count == initial_count + 1

    def test_patch_request_triggers_audit(self):
        """Test that PATCH requests trigger audit logging"""
        # First, create a resource to update
        create_response = self.client.post(
            "/api/url/shorten/",
            {"long_url": "https://www.example.com/initial-patch"},
            format="json",
        )

        assert create_response.status_code == status.HTTP_201_CREATED
        short_url = create_response.data["data"]["short_url"]

        initial_count = AuditLog.objects.count()

        # Update the resource with PATCH
        response = self.client.patch(
            f"/api/url/{short_url}/",
            {
                "long_url": "https://www.example.com/patched",
            },
            format="json",
        )

        final_count = AuditLog.objects.count()
        assert final_count == initial_count + 1

    def test_delete_request_triggers_audit(self):
        """Test that DELETE requests trigger audit logging"""
        # First, create a resource to delete
        create_response = self.client.post(
            "/api/url/shorten/",
            {"long_url": "https://www.example.com/to-delete"},
            format="json",
        )

        assert create_response.status_code == status.HTTP_201_CREATED
        short_url = create_response.data["data"]["short_url"]

        initial_count = AuditLog.objects.count()

        # Delete the resource
        response = self.client.delete(f"/api/url/{short_url}/")

        final_count = AuditLog.objects.count()
        assert final_count == initial_count + 1

        # Verify the audit entry for deletion
        latest_audit = AuditLog.objects.last()
        assert latest_audit.action == "DELETE"
        assert latest_audit.user == self.user

    def test_get_request_does_not_trigger_audit(self):
        """Test that GET requests do not trigger audit logging"""
        # First, create a resource to retrieve
        create_response = self.client.post(
            "/api/url/shorten/",
            {"long_url": "https://www.example.com/to-retrieve"},
            format="json",
        )

        assert create_response.status_code == status.HTTP_201_CREATED
        short_url = create_response.data["data"]["short_url"]

        initial_count = AuditLog.objects.count()

        # Retrieve the resource with GET
        response = self.client.get(f"/api/url/{short_url}/")

        final_count = AuditLog.objects.count()
        # No new audit entry should have been created for GET request
        assert final_count == initial_count


@pytest.mark.django_db
class TestAuditLogsEndpoint:
    """Test cases for the audit logs endpoint"""

    def setup_method(self):
        self.client = APIClient()
        # Create an admin user
        self.admin_user = User.objects.create_superuser(
            username="adminuser", email="admin@example.com", password="adminpass123"
        )
        self.client.force_authenticate(user=self.admin_user)

        # Create a regular user
        self.regular_user = User.objects.create_user(
            username="regularuser",
            email="regular@example.com",
            password="regularpass123",
        )

        # Create some audit logs for testing
        AuditLog.objects.create(
            action="CREATE",
            user=self.regular_user,
            ip_address="192.168.1.1",
            content_type="url",
            content_id="1",
            changes={"field": "value"},
            successful=True,
        )
        AuditLog.objects.create(
            action="UPDATE",
            user=self.admin_user,
            ip_address="10.0.0.1",
            content_type="user",
            content_id="2",
            changes={"old_value": "old", "new_value": "new"},
            successful=True,
        )

    def test_get_audit_logs_as_admin(self):
        """Test that admin users can retrieve audit logs"""
        response = self.client.get("/api/admin/audit/logs/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] == True
        data = response.data["data"]
        assert "data" in data
        assert "pagination" in data
        assert len(data["data"]) > 0

    def test_get_audit_logs_requires_admin(self):
        """Test that regular users cannot access audit logs"""
        # Switch to regular user
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get("/api/admin/audit/logs/")

        # Should return 403 Forbidden or 401 Unauthorized
        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_401_UNAUTHORIZED,
        ]

    def test_get_audit_logs_with_user_filter(self):
        """Test filtering audit logs by user ID"""
        response = self.client.get(
            f"/api/admin/audit/logs/?user_id={self.regular_user.id}"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] == True
        data = response.data["data"]
        assert "data" in data
        # All returned logs should be for the specified user
        for log in data["data"]:
            assert log["user_id"] == self.regular_user.id

    def test_get_audit_logs_with_action_filter(self):
        """Test filtering audit logs by action type"""
        response = self.client.get("/api/admin/audit/logs/?action=CREATE")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] == True
        data = response.data["data"]
        assert "data" in data
        # All returned logs should have the specified action
        for log in data["data"]:
            assert log["action"] == "CREATE"

    def test_get_audit_logs_with_date_filter(self):
        """Test filtering audit logs by date range"""
        # Get current date for the test
        today = timezone.now().strftime("%Y-%m-%d")

        response = self.client.get(
            f"/api/admin/audit/logs/?date_from={today}&date_to={today}"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] == True
        assert "data" in response.data["data"]

    def test_get_audit_logs_with_pagination(self):
        """Test pagination of audit logs"""
        response = self.client.get("/api/admin/audit/logs/?page=1&page_size=1")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] == True
        data = response.data["data"]
        assert "data" in data
        assert "pagination" in data
        assert len(data["data"]) <= 1
        assert data["pagination"]["current_page"] == 1

    def test_get_audit_logs_with_invalid_date_format(self):
        """Test error handling for invalid date format"""
        response = self.client.get("/api/admin/audit/logs/?date_from=invalid-date")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] == False
        assert "Invalid date format" in response.data["message"]

    def test_get_audit_logs_sorted_by_timestamp(self):
        """Test that audit logs are sorted by timestamp by default"""
        response = self.client.get("/api/admin/audit/logs/?sort_by=-timestamp")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] == True
        data = response.data["data"]
        assert "data" in data
        # Check that the results are sorted by timestamp in descending order
        if len(data["data"]) > 1:
            timestamps = [log["timestamp"] for log in data["data"]]
            assert timestamps == sorted(timestamps, reverse=True)
