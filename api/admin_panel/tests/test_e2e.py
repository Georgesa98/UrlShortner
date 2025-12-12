import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from datetime import datetime, timedelta, timezone
from api.analytics.utils import hash_ip
from api.url.models import Url, UrlStatus
from api.analytics.models import Visit
from api.url.services.UrlService import UrlService
from api.url.serializers.UrlSerializer import ShortenUrlSerializer

"""
E2E tests for Admin Panel endpoints
"""

User = get_user_model()


@pytest.mark.django_db
class TestAdminGetUserUrlsEndpoint:
    """Test GET /api/admin/user/{user_id}/urls/ endpoint"""

    def setup_method(self):
        self.client = APIClient()
        # Create admin user
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )
        self.client.force_authenticate(user=self.admin_user)

        # Create regular user with URLs
        self.regular_user = User.objects.create_user(
            username="regularuser",
            email="regular@example.com",
            password="regularpass123",
            role=User.Role.USER,
        )

        # Create some URLs for the regular user
        self.url1 = Url.objects.create(
            long_url="https://www.example.com/first",
            short_url="first123",
            user=self.regular_user,
        )
        self.url2 = Url.objects.create(
            long_url="https://www.example.com/second",
            short_url="second123",
            user=self.regular_user,
        )

        # Create URL status records
        UrlStatus.objects.create(url=self.url1)
        UrlStatus.objects.create(url=self.url2)

    def test_get_user_urls_success(self):
        """Test successful retrieval of user's URLs as admin"""
        url = f"/api/admin/user/urls/{self.regular_user.id}/"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["urls"]) == 2
        assert response.data["pagination"]["total"] == 2
        assert response.data["pagination"]["page"] == 1

    def test_get_user_urls_pagination(self):
        """Test pagination of user's URLs"""
        # Create more URLs to test pagination
        for i in range(10):
            url_obj = Url.objects.create(
                long_url=f"https://www.example.com/test{i}",
                short_url=f"test{i}abc",
                user=self.regular_user,
            )
            UrlStatus.objects.create(url=url_obj)

        url = f"/api/admin/user/urls/{self.regular_user.id}/?limit=5&page=1"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["urls"]) == 5
        assert response.data["pagination"]["total"] == 12  # 2 existing + 10 new
        assert response.data["pagination"]["limit"] == 5
        assert response.data["pagination"]["page"] == 1
        assert response.data["pagination"]["has_next"] is True

    def test_get_user_urls_unauthorized(self):
        """Test retrieval without admin privileges"""
        # Create a regular user and authenticate as them
        regular = User.objects.create_user(
            username="regularuser2",
            email="regular2@example.com",
            password="regularpass123",
            role=User.Role.USER,
        )
        self.client.force_authenticate(user=regular)

        url = f"/api/admin/user/urls/{self.regular_user.id}/"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_user_urls_nonexistent_user(self):
        """Test retrieval for non-existent user"""
        url = "/api/admin/user/nonexistent/urls/"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestAdminBulkUrlDeletionEndpoint:
    """Test POST /api/admin/urls/bulk-delete/ endpoint"""

    def setup_method(self):
        self.client = APIClient()
        # Create admin user
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )
        self.client.force_authenticate(user=self.admin_user)

        # Create regular user with URLs
        self.regular_user = User.objects.create_user(
            username="regularuser",
            email="regular@example.com",
            password="regularpass123",
            role=User.Role.USER,
        )

        # Create URLs to delete
        self.url1 = Url.objects.create(
            long_url="https://www.example.com/first",
            short_url="first123",
            user=self.regular_user,
        )
        self.url2 = Url.objects.create(
            long_url="https://www.example.com/second",
            short_url="second123",
            user=self.regular_user,
        )

    def test_bulk_url_deletion_success(self):
        """Test successful bulk deletion of URLs"""
        url = "/api/admin/urls/bulk-delete/"
        payload = {"url_ids": [self.url1.id, self.url2.id]}

        response = self.client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["deleted_count"] == 2
        assert not Url.objects.filter(id=self.url1.id).exists()
        assert not Url.objects.filter(id=self.url2.id).exists()

    def test_bulk_url_deletion_partial_success(self):
        """Test bulk deletion with some non-existent URLs"""
        url = "/api/admin/urls/bulk-delete/"
        payload = {"url_ids": [self.url1.id, 99999]}  # 99999 is non-existent

        response = self.client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["deleted_count"] == 1
        assert not Url.objects.filter(id=self.url1.id).exists()
        assert Url.objects.filter(id=self.url2.id).exists()

    def test_bulk_url_deletion_unauthorized(self):
        """Test bulk deletion without admin privileges"""
        # Create a regular user and authenticate as them
        regular = User.objects.create_user(
            username="regularuser2",
            email="regular2@example.com",
            password="regularpass123",
            role=User.Role.USER,
        )
        self.client.force_authenticate(user=regular)

        url = "/api/admin/urls/bulk-delete/"
        payload = {"url_ids": [self.url1.id]}

        response = self.client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Url.objects.filter(id=self.url1.id).exists()  # Not deleted


@pytest.mark.django_db
class TestAdminBulkFlagUrlEndpoint:
    """Test POST /api/admin/urls/bulk-flag/ endpoint"""

    def setup_method(self):
        self.client = APIClient()
        # Create admin user
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )
        self.client.force_authenticate(user=self.admin_user)

        # Create regular user with URLs
        self.regular_user = User.objects.create_user(
            username="regularuser",
            email="regular@example.com",
            password="regularpass123",
            role=User.Role.USER,
        )

        # Create URLs to flag
        self.url1 = Url.objects.create(
            long_url="https://www.example.com/first",
            short_url="first123",
            user=self.regular_user,
        )
        self.url2 = Url.objects.create(
            long_url="https://www.example.com/second",
            short_url="second123",
            user=self.regular_user,
        )

        # Create URL status records
        self.status1 = UrlStatus.objects.create(
            url=self.url1, state=UrlStatus.State.ACTIVE
        )
        self.status2 = UrlStatus.objects.create(
            url=self.url2, state=UrlStatus.State.ACTIVE
        )

    def test_bulk_flag_url_success(self):
        """Test successful bulk flagging of URLs"""
        url = "/api/admin/urls/bulk-flag/"
        payload = {
            "data": [
                {"url_id": str(self.url1.id), "state": "flagged", "reason": "spam"},
                {
                    "url_id": str(self.url2.id),
                    "state": "disabled",
                    "reason": "policy violation",
                },
            ]
        }

        response = self.client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success_count"] == 2
        assert len(response.data["failed_items"]) == 0

        # Verify changes in database
        self.status1.refresh_from_db()
        self.status2.refresh_from_db()
        assert self.status1.state == UrlStatus.State.FLAGGED
        assert self.status1.reason == "spam"
        assert self.status2.state == UrlStatus.State.DISABLED
        assert self.status2.reason == "policy violation"

    def test_bulk_flag_url_partial_success(self):
        """Test bulk flag with some non-existent URLs"""
        url = "/api/admin/urls/bulk-flag/"
        payload = {
            "data": [
                {"url_id": str(self.url1.id), "state": "flagged", "reason": "spam"},
                {
                    "url_id": "nonexistent",
                    "state": "disabled",
                    "reason": "policy violation",
                },
            ]
        }

        response = self.client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success_count"] == 1
        assert len(response.data["failed_items"]) == 1

        # Verify that the valid URL was updated
        self.status1.refresh_from_db()
        assert self.status1.state == UrlStatus.State.FLAGGED
        assert self.status1.reason == "spam"


@pytest.mark.django_db
class TestAdminGetUrlDetailsEndpoint:
    """Test GET /api/admin/url/{url_id}/details/ endpoint"""

    def setup_method(self):
        self.client = APIClient()
        # Create admin user
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )
        self.client.force_authenticate(user=self.admin_user)

        # Create regular user with a URL
        self.regular_user = User.objects.create_user(
            username="regularuser",
            email="regular@example.com",
            password="regularpass123",
            role=User.Role.USER,
        )

        # Create URL and status
        self.url = Url.objects.create(
            long_url="https://www.example.com/test",
            short_url="test123",
            user=self.regular_user,
        )
        self.url_status = UrlStatus.objects.create(
            url=self.url, state=UrlStatus.State.ACTIVE, reason="test reason"
        )

        # Create some visits for the URL
        for i in range(5):
            Visit.objects.create(
                url=self.url,
                hashed_ip=hash_ip(f"192.168.1.{i}"),
                referrer="referrer.example.com",
                browser="Chrome",
                operating_system="Windows",
            )

    def test_get_url_details_success(self):
        """Test successful retrieval of URL details"""
        url = f"/api/admin/url/details/{self.url.id}/"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "url" in response.data
        assert "url_status" in response.data
        assert "recent_clicks" in response.data
        assert len(response.data["recent_clicks"]) <= 10  # Limited to 10 in service

    def test_get_url_details_unauthorized(self):
        """Test URL details retrieval without admin privileges"""
        # Create a regular user and authenticate as them
        regular = User.objects.create_user(
            username="regularuser2",
            email="regular2@example.com",
            password="regularpass123",
            role=User.Role.USER,
        )
        self.client.force_authenticate(user=regular)

        url = f"/api/admin/url/details/{self.url.id}/"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestAdminSearchUrlsEndpoint:
    """Test GET /api/admin/urls/search/ endpoint"""

    def setup_method(self):
        self.client = APIClient()
        # Create admin user
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )
        self.client.force_authenticate(user=self.admin_user)

        # Create regular user with URLs
        self.regular_user = User.objects.create_user(
            username="regularuser",
            email="regular@example.com",
            password="regularpass123",
            role=User.Role.USER,
        )

        # Create URLs with different names
        self.url1 = Url.objects.create(
            long_url="https://www.example.com/first",
            short_url="first123",
            name="First URL",
            user=self.regular_user,
        )
        self.url2 = Url.objects.create(
            long_url="https://www.example.com/second",
            short_url="second123",
            name="Second URL",
            user=self.regular_user,
        )
        self.url3 = Url.objects.create(
            long_url="https://www.anotherdomain.com/test",
            short_url="other123",
            name="Other URL",
            user=self.regular_user,
        )

        # Create URL status records
        UrlStatus.objects.create(url=self.url1)
        UrlStatus.objects.create(url=self.url2)
        UrlStatus.objects.create(url=self.url3)

    def test_search_urls_by_name(self):
        """Test searching URLs by name"""
        url = "/api/admin/urls/search/?q=First"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["pagination"]["total"] >= 1
        assert any(item["name"] == "First URL" for item in response.data["urls"])

    def test_search_urls_by_short_url(self):
        """Test searching URLs by short URL"""
        url = "/api/admin/urls/search/?q=second123"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["pagination"]["total"] >= 1
        assert any(item["short_url"] == "second123" for item in response.data["urls"])

    def test_search_urls_by_long_url(self):
        """Test searching URLs by long URL"""
        url = "/api/admin/urls/search/?q=anotherdomain"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["pagination"]["total"] >= 1
        assert any(
            "anotherdomain.com" in item["long_url"] for item in response.data["urls"]
        )

    def test_search_urls_pagination(self):
        """Test pagination of search results"""
        url = "/api/admin/urls/search/?q=URL&limit=2&page=1"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["urls"]) == 2
        assert response.data["pagination"]["total"] == 3
        assert response.data["pagination"]["limit"] == 2
        assert response.data["pagination"]["page"] == 1

    def test_search_urls_empty_query(self):
        """Test search with empty query parameter"""
        url = "/api/admin/urls/search/?q="

        response = self.client.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestAdminUpdateUrlDestinationEndpoint:
    """Test PATCH /api/admin/url/{short_url}/destination/ endpoint"""

    def setup_method(self):
        self.client = APIClient()
        # Create admin user
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )
        self.client.force_authenticate(user=self.admin_user)

        # Create regular user with a URL
        self.regular_user = User.objects.create_user(
            username="regularuser",
            email="regular@example.com",
            password="regularpass123",
            role=User.Role.USER,
        )

        # Create URL
        self.url = Url.objects.create(
            long_url="https://www.example.com/old",
            short_url="test123",
            user=self.regular_user,
        )

    def test_update_url_destination_success(self):
        """Test successful update of URL destination"""
        url = f"/api/admin/url/destination/{self.url.short_url}/"
        payload = {"new_destination": "https://www.example.com/new"}

        response = self.client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["long_url"] == "https://www.example.com/new"

        # Verify in database
        self.url.refresh_from_db()
        assert self.url.long_url == "https://www.example.com/new"

    def test_update_url_destination_unauthorized(self):
        """Test URL destination update without admin privileges"""
        # Create a regular user and authenticate as them
        regular = User.objects.create_user(
            username="regularuser2",
            email="regular2@example.com",
            password="regularpass123",
            role=User.Role.USER,
        )
        self.client.force_authenticate(user=regular)

        url = f"/api/admin/url/destination/{self.url.short_url}/"
        payload = {"new_destination": "https://www.example.com/hacked"}

        response = self.client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        self.url.refresh_from_db()
        assert self.url.long_url == "https://www.example.com/old"  # Not changed


@pytest.mark.django_db
class TestAdminGetUsersEndpoint:
    """Test GET /api/admin/users/ endpoint"""

    def setup_method(self):
        self.client = APIClient()
        # Create admin user
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )
        self.client.force_authenticate(user=self.admin_user)

        # Create users with different roles
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="userpass123",
            role=User.Role.USER,
            first_name="John",
            last_name="Doe",
        )
        self.staff_user = User.objects.create_user(
            username="staff1",
            email="staff@example.com",
            password="staffpass123",
            role=User.Role.STAFF,
            first_name="Jane",
            last_name="Smith",
        )
        self.admin_user2 = User.objects.create_user(
            username="admin2",
            email="admin2@example.com",
            password="adminpass123",
            role=User.Role.ADMIN,
            first_name="Bob",
            last_name="Johnson",
        )

    def test_get_users_success(self):
        """Test successful retrieval of users"""
        url = "/api/admin/users/"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["pagination"]["total"] >= 3
        assert len(response.data["users"]) > 0

    def test_get_users_with_role_filter(self):
        """Test retrieval of users with role filter"""
        url = "/api/admin/users/?roles=USER"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert all(user["role"] == "USER" for user in response.data["users"])

    def test_get_users_with_active_filter(self):
        """Test retrieval of users with active filter"""
        url = "/api/admin/users/?is_active=true"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert all(user["is_active"] == True for user in response.data["users"])

    def test_get_users_pagination(self):
        """Test pagination of users"""
        url = "/api/admin/users/?limit=2&page=1"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["users"]) == 2
        assert response.data["pagination"]["limit"] == 2
        assert response.data["pagination"]["page"] == 1

    def test_get_users_unauthorized(self):
        """Test user retrieval without admin privileges"""
        # Create a regular user and authenticate as them
        regular = User.objects.create_user(
            username="regularuser2",
            email="regular2@example.com",
            password="regularpass123",
            role=User.Role.USER,
        )
        self.client.force_authenticate(user=regular)

        url = "/api/admin/users/"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestAdminToggleBanUserEndpoint:
    """Test PATCH /api/admin/user/{user_id}/ban/ endpoint"""

    def setup_method(self):
        self.client = APIClient()
        # Create admin user
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )
        self.client.force_authenticate(user=self.admin_user)

        # Create regular user to ban
        self.regular_user = User.objects.create_user(
            username="regularuser",
            email="regular@example.com",
            password="regularpass123",
            role=User.Role.USER,
        )

    def test_toggle_ban_user_success(self):
        """Test successful toggling of ban status"""
        url = f"/api/admin/user/{self.regular_user.id}/ban/"

        # Verify user is active initially
        assert self.regular_user.is_active == True

        response = self.client.patch(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_active"] == False  # Should now be banned

        # Verify in database
        self.regular_user.refresh_from_db()
        assert self.regular_user.is_active == False

        # Toggle again to unban
        response = self.client.patch(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_active"] == True  # Should now be unbanned

    def test_toggle_ban_user_unauthorized(self):
        """Test ban toggle without admin privileges"""
        # Create a regular user and authenticate as them
        regular = User.objects.create_user(
            username="regularuser2",
            email="regular2@example.com",
            password="regularpass123",
            role=User.Role.USER,
        )
        self.client.force_authenticate(user=regular)

        url = f"/api/admin/user/{self.regular_user.id}/ban/"

        response = self.client.patch(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        self.regular_user.refresh_from_db()
        assert self.regular_user.is_active == True  # Not changed


@pytest.mark.django_db
class TestAdminBulkUserDeletionEndpoint:
    """Test POST /api/admin/users/bulk-delete/ endpoint"""

    def setup_method(self):
        self.client = APIClient()
        # Create admin user
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )
        self.client.force_authenticate(user=self.admin_user)

        # Create users to delete
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="userpass123",
            role=User.Role.USER,
        )
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="userpass123",
            role=User.Role.USER,
        )

    def test_bulk_user_deletion_success(self):
        """Test successful bulk deletion of users"""
        url = "/api/admin/users/bulk-delete/"
        payload = {"user_ids": [self.user1.id, self.user2.id]}

        response = self.client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["deleted_count"] == 2
        assert not User.objects.filter(id=self.user1.id).exists()
        assert not User.objects.filter(id=self.user2.id).exists()

    def test_bulk_user_deletion_unauthorized(self):
        """Test bulk deletion without admin privileges"""
        # Create a regular user and authenticate as them
        regular = User.objects.create_user(
            username="regularuser2",
            email="regular2@example.com",
            password="regularpass123",
            role=User.Role.USER,
        )
        self.client.force_authenticate(user=regular)

        url = "/api/admin/users/bulk-delete/"
        payload = {"user_ids": [self.user1.id]}

        response = self.client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert User.objects.filter(id=self.user1.id).exists()  # Not deleted


@pytest.mark.django_db
class TestAdminGetUserDetailsEndpoint:
    """Test GET /api/admin/user/{user_id}/details/ endpoint"""

    def setup_method(self):
        self.client = APIClient()
        # Create admin user
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )
        self.client.force_authenticate(user=self.admin_user)

        # Create regular user with URLs
        self.regular_user = User.objects.create_user(
            username="regularuser",
            email="regular@example.com",
            password="regularpass123",
            role=User.Role.USER,
            first_name="John",
            last_name="Doe",
        )

        # Create some URLs for the user
        self.url1 = Url.objects.create(
            long_url="https://www.example.com/first",
            short_url="first123",
            user=self.regular_user,
        )
        self.url2 = Url.objects.create(
            long_url="https://www.example.com/second",
            short_url="second123",
            user=self.regular_user,
        )

    def test_get_user_details_success(self):
        """Test successful retrieval of user details"""
        url = f"/api/admin/user/details/{self.regular_user.id}/"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "user" in response.data
        assert "urls" in response.data
        assert response.data["user"]["id"] == self.regular_user.id
        assert response.data["user"]["username"] == "regularuser"
        assert len(response.data["urls"]) == 2

    def test_get_user_details_unauthorized(self):
        """Test user details retrieval without admin privileges"""
        # Create a regular user and authenticate as them
        regular = User.objects.create_user(
            username="regularuser2",
            email="regular2@example.com",
            password="regularpass123",
            role=User.Role.USER,
        )
        self.client.force_authenticate(user=regular)

        url = f"/api/admin/user/details/{self.regular_user.id}/"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestAdminSearchUsersEndpoint:
    """Test GET /api/admin/users/search/ endpoint"""

    def setup_method(self):
        self.client = APIClient()
        # Create admin user
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )
        self.client.force_authenticate(user=self.admin_user)

        # Create users to search
        self.user1 = User.objects.create_user(
            username="john_doe",
            email="john@example.com",
            password="pass123",
            role=User.Role.USER,
            first_name="John",
            last_name="Doe",
        )
        self.user2 = User.objects.create_user(
            username="jane_smith",
            email="jane@example.com",
            password="pass123",
            role=User.Role.USER,
            first_name="Jane",
            last_name="Smith",
        )

    def test_search_users_by_username(self):
        """Test searching users by username"""
        url = "/api/admin/users/search/?q=john"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["pagination"]["total"] >= 1
        assert any(user["username"] == "john_doe" for user in response.data["users"])

    def test_search_users_by_first_name(self):
        """Test searching users by first name"""
        url = "/api/admin/users/search/?q=Jane"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["pagination"]["total"] >= 1
        assert any(user["first_name"] == "Jane" for user in response.data["users"])

    def test_search_users_by_last_name(self):
        """Test searching users by last name"""
        url = "/api/admin/users/search/?q=Doe"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["pagination"]["total"] >= 1
        assert any(user["last_name"] == "Doe" for user in response.data["users"])

    def test_search_users_pagination(self):
        """Test pagination of user search results"""
        url = "/api/admin/users/search/?q=John&limit=1&page=1"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["users"]) == 1
        assert response.data["pagination"]["limit"] == 1
        assert response.data["pagination"]["page"] == 1

    def test_search_users_empty_query(self):
        """Test search with empty query parameter"""
        url = "/api/admin/users/search/?q="

        response = self.client.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_search_users_unauthorized(self):
        """Test user search without admin privileges"""
        # Create a regular user and authenticate as them
        regular = User.objects.create_user(
            username="regularuser2",
            email="regular2@example.com",
            password="regularpass123",
            role=User.Role.USER,
        )
        self.client.force_authenticate(user=regular)

        url = "/api/admin/users/search/?q=john"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
