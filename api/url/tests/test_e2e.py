import redis
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from datetime import datetime, timedelta, timezone
from api.url.models import Url, UrlStatus

"""
E2E tests for Url management endpoints
"""

User = get_user_model()


@pytest.mark.django_db
class TestURLShortenEndpoint:
    """Test POST /api/url/shorten/ endpoint"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/api/url/shorten/"

    def test_shorten_url_success(self):
        """Test successful Url shortening"""
        payload = {"long_url": "https://www.example.com/very/long/url/path"}

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "short_url" in response.data
        assert response.data["long_url"] == payload["long_url"]
        assert response.data["user"] == self.user.id
        assert response.data["visits"] == 0
        assert "created_at" in response.data
        assert "updated_at" in response.data
        assert response.data["url_status"]["state"] == "active"
        assert response.data["last_accessed"] is None

    def test_shorten_url_with_expiry(self):
        """Test Url shortening with expiry date"""
        expiry = datetime.now(timezone.utc) + timedelta(days=30)
        payload = {
            "long_url": "https://www.example.com/temporary",
            "expiry_date": expiry.isoformat(),
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["expiry_date"] is not None
        assert response.data["days_until_expiry"] is not None

    def test_shorten_url_unauthenticated(self):
        """Test Url shortening without authentication"""
        self.client.force_authenticate(user=None)
        payload = {"long_url": "https://www.example.com"}

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_shorten_url_invalid_format(self):
        """Test Url shortening with invalid Url format"""
        payload = {"long_url": "not-a-valid-url"}

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_shorten_url_missing_field(self):
        """Test Url shortening without required field"""
        payload = {}

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestURLRetrieveEndpoint:
    """Test GET /api/url/{short_url}/ endpoint"""

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
            long_url="https://www.example.com/test", short_url="test123", user=self.user
        )

    def test_retrieve_url_success(self):
        """Test successful Url retrieval by owner"""
        url = f"/api/url/{self.url_obj.short_url}/"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["short_url"] == self.url_obj.short_url
        assert response.data["long_url"] == self.url_obj.long_url
        assert response.data["user"] == self.user.id

    def test_retrieve_url_not_owner(self):
        """Test Url retrieval by non-owner"""
        self.client.force_authenticate(user=self.other_user)
        url = f"/api/url/{self.url_obj.short_url}/"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_retrieve_url_not_found(self):
        """Test retrieval of non-existent Url"""
        url = "/api/url/nonexistent/"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_url_unauthenticated(self):
        """Test Url retrieval without authentication"""
        self.client.force_authenticate(user=None)
        url = f"/api/url/{self.url_obj.short_url}/"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestURLUpdateEndpoint:
    """Test PATCH /api/url/{short_url}/ endpoint"""

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
            long_url="https://www.example.com/original",
            short_url="update123",
            user=self.user,
        )

    def test_update_url_expiry_success(self):
        """Test successful Url expiry date update"""
        url = f"/api/url/{self.url_obj.short_url}/"
        new_expiry = datetime.now(timezone.utc) + timedelta(days=60)
        payload = {"expiry_date": new_expiry.isoformat()}

        response = self.client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["expiry_date"] is not None

    def test_update_url_long_url_success(self):
        """Test successful long Url update"""
        url = f"/api/url/{self.url_obj.short_url}/"
        payload = {"long_url": "https://www.example.com/updated"}

        response = self.client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["long_url"] == payload["long_url"]

    def test_update_url_not_owner(self):
        """Test Url update by non-owner"""
        self.client.force_authenticate(user=self.other_user)
        url = f"/api/url/{self.url_obj.short_url}/"
        payload = {"long_url": "https://www.example.com/hacked"}

        response = self.client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_url_not_found(self):
        """Test update of non-existent Url"""
        url = "/api/url/nonexistent/"
        payload = {"long_url": "https://www.example.com/new"}

        response = self.client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_url_unauthenticated(self):
        """Test Url update without authentication"""
        self.client.force_authenticate(user=None)
        url = f"/api/url/{self.url_obj.short_url}/"
        payload = {"long_url": "https://www.example.com/new"}

        response = self.client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestURLDeleteEndpoint:
    """Test DELETE /api/url/{short_url}/ endpoint"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

    def test_delete_url_success(self):
        """Test successful Url deletion by owner"""
        url_obj = Url.objects.create(
            long_url="https://www.example.com/delete",
            short_url="delete123",
            user=self.user,
        )
        url = f"/api/url/{url_obj.short_url}/"

        response = self.client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Url.objects.filter(short_url="delete123").exists()

    def test_delete_url_not_owner(self):
        """Test Url deletion by non-owner"""
        url_obj = Url.objects.create(
            long_url="https://www.example.com/protected",
            short_url="protected123",
            user=self.user,
        )
        self.client.force_authenticate(user=self.other_user)
        url = f"/api/url/{url_obj.short_url}/"

        response = self.client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Url.objects.filter(short_url="protected123").exists()

    def test_delete_url_not_found(self):
        """Test deletion of non-existent Url"""
        url = "/api/url/nonexistent/"

        response = self.client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_url_unauthenticated(self):
        """Test Url deletion without authentication"""
        url_obj = Url.objects.create(
            long_url="https://www.example.com/auth", short_url="auth123", user=self.user
        )
        self.client.force_authenticate(user=None)
        url = f"/api/url/{url_obj.short_url}/"

        response = self.client.delete(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Url.objects.filter(short_url="auth123").exists()


@pytest.mark.django_db
class TestURLRedirectEndpoint:
    """Test GET /api/url/redirect/{short_url} endpoint"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.url_obj = Url.objects.create(
            long_url="https://www.example.com/redirect",
            short_url="redir123",
            user=self.user,
        )
        self.url_status_obj = UrlStatus.objects.create(url=self.url_obj)

    def test_redirect_success(self):
        """Test successful redirect to long Url"""
        url = f"/api/url/redirect/{self.url_obj.short_url}/"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_302_FOUND
        assert response["Location"] == self.url_obj.long_url

        # Verify visit count incremented
        self.url_obj.refresh_from_db()
        assert self.url_obj.visits == 1
        assert self.url_obj.last_accessed is not None

    def test_redirect_not_found(self):
        """Test redirect with non-existent short Url"""
        url = "/api/url/redirect/nonexistent/"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_redirect_expired_url(self):
        """Test redirect with expired Url"""
        expired_url = Url.objects.create(
            long_url="https://www.example.com/expired",
            short_url="expired123",
            user=self.user,
            expiry_date=datetime.now(timezone.utc) - timedelta(days=1),
        )
        UrlStatus.objects.create(url=expired_url, state=UrlStatus.State.EXPIRED)
        url = f"/api/url/redirect/{expired_url.short_url}/"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_410_GONE

    def test_redirect_no_authentication_required(self):
        """Test redirect works without authentication"""
        url = f"/api/url/redirect/{self.url_obj.short_url}/"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_302_FOUND

    def test_redirect_increments_visits(self):
        """Test multiple redirects increment visit counter"""
        url = f"/api/url/redirect/{self.url_obj.short_url}/"
        initial_visits = self.url_obj.visits

        for _ in range(3):
            response = self.client.get(url)
            assert response.status_code == status.HTTP_302_FOUND

        self.url_obj.refresh_from_db()
        assert self.url_obj.visits == initial_visits + 3


@pytest.mark.django_db
class TestURLEndpointsIntegration:
    """Integration tests for complete Url workflows"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

    def test_complete_url_lifecycle(self):
        """Test creating, retrieving, updating, and deleting a Url"""
        # Create Url
        create_payload = {"long_url": "https://www.example.com/lifecycle"}
        create_response = self.client.post(
            "/api/url/shorten/", create_payload, format="json"
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        short_url = create_response.data["short_url"]

        # Retrieve Url
        retrieve_response = self.client.get(f"/api/url/{short_url}/")
        assert retrieve_response.status_code == status.HTTP_200_OK
        assert retrieve_response.data["long_url"] == create_payload["long_url"]

        # Update Url
        update_payload = {"long_url": "https://www.example.com/updated"}
        update_response = self.client.patch(
            f"/api/url/{short_url}/", update_payload, format="json"
        )
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.data["long_url"] == update_payload["long_url"]

        # Delete Url
        delete_response = self.client.delete(f"/api/url/{short_url}/")
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        verify_response = self.client.get(f"/api/url/{short_url}/")
        assert verify_response.status_code == status.HTTP_404_NOT_FOUND

    def test_url_with_redirect_workflow(self):
        """Test Url creation and redirect functionality"""
        # Create Url
        create_payload = {"long_url": "https://www.example.com/workflow"}
        create_response = self.client.post(
            "/api/url/shorten/", create_payload, format="json"
        )
        short_url = create_response.data["short_url"]

        # Test redirect
        redirect_response = self.client.get(f"/api/url/redirect/{short_url}/")
        assert redirect_response.status_code == status.HTTP_302_FOUND

        # Verify visit count updated
        retrieve_response = self.client.get(f"/api/url/{short_url}/")
        assert retrieve_response.data["visits"] > 0
