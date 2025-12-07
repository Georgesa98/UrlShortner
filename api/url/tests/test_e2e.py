import redis
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from datetime import datetime, timedelta, timezone
from api.url.models import Url, UrlStatus
import io
from PIL import Image
from django.core.cache import cache
from api.url.services.ShortCodeService import ShortCodeService
from unittest.mock import patch


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


@pytest.mark.django_db
class TestCustomAliasFeature:
    """Test custom alias functionality for Url shortening"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        cache.clear()

    def teardown_method(self):
        cache.clear()

    def test_create_url_with_custom_alias(self):
        """Test creating a Url with custom alias"""
        url = "/api/url/shorten/"
        payload = {
            "long_url": "https://www.example.com/custom-test",
            "short_url": "my-custom-link",
        }

        response = self.client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["short_url"] == "my-custom-link"
        assert response.data["is_custom_alias"] is True
        assert response.data["long_url"] == payload["long_url"]

        # Verify in database
        url_obj = Url.objects.get(short_url="my-custom-link")
        assert url_obj.is_custom_alias is True
        assert url_obj.long_url == payload["long_url"]

    def test_custom_alias_must_be_unique(self):
        """Test that custom alias must be unique"""
        url = "/api/url/shorten/"

        # Create first Url with custom alias
        payload1 = {
            "long_url": "https://www.example.com/first",
            "short_url": "unique-alias",
        }
        response1 = self.client.post(url, payload1, format="json")
        assert response1.status_code == status.HTTP_201_CREATED

        # Try to create second Url with same alias
        payload2 = {
            "long_url": "https://www.example.com/second",
            "short_url": "unique-alias",
        }
        response2 = self.client.post(url, payload2, format="json")

        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            "custom_alias" in str(response2.data).lower()
            or "alias" in str(response2.data).lower()
        )

    def test_custom_alias_validation(self):
        """Test custom alias validation rules"""
        url = "/api/url/shorten/"

        # Test invalid characters
        invalid_aliases = [
            "alias with spaces",
            "alias@special",
            "alias/slash",
            "alias\\backslash",
            "alias?query",
            "alias#hash",
        ]

        for invalid_alias in invalid_aliases:
            payload = {
                "long_url": "https://www.example.com/test",
                "short_url": invalid_alias,
            }
            response = self.client.post(url, payload, format="json")

            assert (
                response.status_code == status.HTTP_400_BAD_REQUEST
            ), f"Alias '{invalid_alias}' should be invalid"

    def test_custom_alias_valid_formats(self):
        """Test valid custom alias formats"""
        url = "/api/url/shorten/"

        valid_aliases = [
            "simplexxx",
            "with-dashes",
            "with_underscores",
            "MixedCase123",
            "numbers123",
        ]

        for valid_alias in valid_aliases:
            payload = {
                "long_url": f"https://www.example.com/test-{valid_alias}",
                "short_url": valid_alias,
            }
            response = self.client.post(url, payload, format="json")

            assert (
                response.status_code == status.HTTP_201_CREATED
            ), f"Alias '{valid_alias}' should be valid. Got: {response.data}"
            assert response.data["short_url"] == valid_alias

    def test_custom_alias_length_limits(self):
        """Test custom alias length validation"""
        url = "/api/url/shorten/"

        # Test too short (if there's a minimum)
        payload_short = {
            "long_url": "https://www.example.com/test",
            "short_url": "ab",  # 2 characters
        }
        response_short = self.client.post(url, payload_short, format="json")
        # This might pass or fail depending on your validation rules

        # Test too long
        payload_long = {
            "long_url": "https://www.example.com/test",
            "short_url": "a" * 100,  # Very long alias
        }
        response_long = self.client.post(url, payload_long, format="json")
        assert response_long.status_code == status.HTTP_400_BAD_REQUEST

    def test_custom_alias_redirect_works(self):
        """Test that custom alias redirects properly"""
        # Create Url with custom alias
        create_url = "/api/url/shorten/"
        payload = {
            "long_url": "https://www.example.com/redirect-test",
            "short_url": "redirect-me",
        }
        create_response = self.client.post(create_url, payload, format="json")
        assert create_response.status_code == status.HTTP_201_CREATED

        # Test redirect
        redirect_url = "/api/url/redirect/redirect-me/"
        redirect_response = self.client.get(redirect_url)

        assert redirect_response.status_code == status.HTTP_302_FOUND
        assert redirect_response["Location"] == payload["long_url"]

    def test_url_without_custom_alias_uses_generated(self):
        """Test that URLs without custom alias get auto-generated short_url"""
        url = "/api/url/shorten/"
        payload = {"long_url": "https://www.example.com/auto-generated"}

        response = self.client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["is_custom_alias"] is False
        assert len(response.data["short_url"]) > 0
        assert response.data["short_url"] != payload["long_url"]

    def test_update_url_custom_alias(self):
        """Test updating a Url's custom alias"""
        # Create Url with custom alias
        create_url = "/api/url/shorten/"
        payload = {
            "long_url": "https://www.example.com/update-test",
            "custom_alias": "original-alias",
        }
        create_response = self.client.post(create_url, payload, format="json")
        short_url = create_response.data["short_url"]

        # Try to update the alias (this might not be allowed depending on your logic)
        update_url = f"/api/url/{short_url}/"
        update_payload = {"custom_alias": "new-alias"}
        update_response = self.client.patch(update_url, update_payload, format="json")

        # This test depends on whether you allow alias updates
        # Adjust assertion based on your business logic
        assert update_response.status_code in [
            status.HTTP_200_OK,  # If updates are allowed
            status.HTTP_400_BAD_REQUEST,  # If updates are not allowed
        ]

    def test_custom_alias_case_sensitivity(self):
        """Test if custom aliases are case-sensitive"""
        url = "/api/url/shorten/"

        # Create with lowercase
        payload1 = {
            "long_url": "https://www.example.com/lower",
            "custom_alias": "testcase",
        }
        response1 = self.client.post(url, payload1, format="json")
        assert response1.status_code == status.HTTP_201_CREATED

        # Try with uppercase
        payload2 = {
            "long_url": "https://www.example.com/upper",
            "custom_alias": "TESTCASE",
        }
        response2 = self.client.post(url, payload2, format="json")

        # Depending on your implementation, this might be:
        # - Rejected as duplicate (case-insensitive)
        # - Accepted as different (case-sensitive)
        assert response2.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST,
        ]


@pytest.mark.django_db
class TestQRCodeGeneration:
    """Test QR code generation feature"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

        # Create a test Url
        self.test_url = Url.objects.create(
            long_url="https://www.example.com/qr-test",
            short_url="qrtest123",
            user=self.user,
        )
        cache.clear()

    def teardown_method(self):
        cache.clear()

    def test_generate_qr_code_success(self):
        """Test successful QR code generation"""
        url = f"/api/url/qr/{self.test_url.short_url}/"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response["Content-Type"] == "image/png"

        # Verify it's a valid image
        try:
            image = Image.open(io.BytesIO(response.content))
            assert image.format == "PNG"
            assert image.size[0] > 0  # Width > 0
            assert image.size[1] > 0  # Height > 0
        except Exception as e:
            pytest.fail(f"Invalid image returned: {e}")

    def test_qr_code_for_nonexistent_url(self):
        """Test QR code generation for non-existent Url"""
        url = "/api/url/qr/nonexistent/"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_qr_code_contains_correct_url(self):
        """Test that QR code contains the correct Url"""
        url = f"/api/url/qr/{self.test_url.short_url}/"

        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

        # Try to decode QR code (requires pyzbar or similar library)
        # This is optional - just verify we get valid image data
        try:
            image = Image.open(io.BytesIO(response.content))
            from pyzbar.pyzbar import decode

            decoded = decode(image)
            assert len(decoded) > 0
            assert self.test_url.short_url in decoded[0].data.decode()

            # For now, just verify image properties
            assert image.format == "PNG"
        except Exception as e:
            pytest.fail(f"Could not process QR code image: {e}")

    def test_qr_code_does_not_save_to_disk(self):
        """Test that QR code is generated in memory, not saved to disk"""
        import os
        import tempfile

        # Get temp directory
        temp_dir = tempfile.gettempdir()

        # List files before
        files_before = set(os.listdir(temp_dir))

        # Generate QR code
        url = f"/api/url/qr/{self.test_url.short_url}/"
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

        # List files after
        files_after = set(os.listdir(temp_dir))

        # No new files should be created
        new_files = files_after - files_before
        qr_files = [f for f in new_files if "qr" in f.lower() or "png" in f.lower()]

        assert (
            len(qr_files) == 0
        ), f"QR code should not be saved to disk. Found: {qr_files}"

    def test_qr_code_no_authentication_required(self):
        """Test QR code generation without authentication (if public)"""
        self.client.force_authenticate(user=None)

        url = f"/api/url/qr/{self.test_url.short_url}/"
        response = self.client.get(url)

        # Depending on your implementation, this might require auth or not
        # Adjust based on your business logic
        assert response.status_code in [
            status.HTTP_200_OK,  # If public
            status.HTTP_401_UNAUTHORIZED,  # If requires auth
        ]

    def test_qr_code_with_custom_alias(self):
        """Test QR code generation for Url with custom alias"""
        # Create Url with custom alias
        custom_url = Url.objects.create(
            long_url="https://www.example.com/custom-qr",
            short_url="custom-qr-alias",
            user=self.user,
            is_custom_alias=True,
        )

        url = f"/api/url/qr/{custom_url.short_url}/"
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response["Content-Type"] == "image/png"

    def test_qr_code_image_size(self):
        """Test QR code image dimensions"""
        url = f"/api/url/qr/{self.test_url.short_url}/"

        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

        image = Image.open(io.BytesIO(response.content))

        # Typical QR code sizes (adjust based on your implementation)
        assert image.size[0] >= 100  # Minimum width
        assert image.size[1] >= 100  # Minimum height
        assert image.size[0] == image.size[1]  # Should be square

    def test_qr_code_response_headers(self):
        """Test QR code response headers"""
        url = f"/api/url/qr/{self.test_url.short_url}/"

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response["Content-Type"] == "image/png"

        # Check for cache headers (optional)
        # assert 'Cache-Control' in response
        # assert 'ETag' in response or 'Last-Modified' in response

    def test_qr_code_multiple_requests_consistent(self):
        """Test that multiple QR code requests return consistent results"""
        url = f"/api/url/qr/{self.test_url.short_url}/"

        # Generate QR code twice
        response1 = self.client.get(url)
        response2 = self.client.get(url)

        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK

        # Content should be identical (or very similar)
        # Exact match might not be guaranteed if timestamps are included
        assert len(response1.content) > 0
        assert len(response2.content) > 0

        # Sizes should be the same
        image1 = Image.open(io.BytesIO(response1.content))
        image2 = Image.open(io.BytesIO(response2.content))
        assert image1.size == image2.size


@pytest.mark.django_db
class TestBatchURLShortening:
    """Test batch Url shortening feature"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/api/url/batch-shorten/"
        cache.clear()

    def teardown_method(self):
        cache.clear()

    def test_batch_shorten_multiple_urls(self):
        """Test shortening multiple URLs in one request"""
        payload = [
            {"long_url": "https://www.example.com/batch1"},
            {"long_url": "https://www.example.com/batch2"},
            {"long_url": "https://www.example.com/batch3"},
        ]

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        # Get the results array (adjust key based on your implementation)
        results = response.data

        assert len(results) == 3

        # Verify each Url was created
        for i, result in enumerate(results):
            assert "short_url" in result
            assert "long_url" in result
            assert result["long_url"] == payload[i]["long_url"]
            assert len(result["short_url"]) > 0

    def test_batch_shorten_with_custom_aliases(self):
        """Test batch shortening with custom aliases"""
        payload = [
            {
                "long_url": "https://www.example.com/batch-custom1",
                "short_url": "batch-alias-1",
            },
            {
                "long_url": "https://www.example.com/batch-custom2",
                "short_url": "batch-alias-2",
            },
        ]

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        results = response.data

        assert len(results) == 2

        # Verify custom aliases were used
        assert results[0]["short_url"] == "batch-alias-1"
        assert results[1]["short_url"] == "batch-alias-2"
        assert results[0]["is_custom_alias"] is True
        assert results[1]["is_custom_alias"] is True

    def test_batch_shorten_mixed_custom_and_auto(self):
        """Test batch with mix of custom aliases and auto-generated"""
        payload = [
            {
                "long_url": "https://www.example.com/mixed1",
                "short_url": "custom-mixed",
            },
            {
                "long_url": "https://www.example.com/mixed2"
                # No custom_alias - should auto-generate
            },
        ]

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        results = response.data

        # First should have custom alias
        assert results[0]["short_url"] == "custom-mixed"
        assert results[0]["is_custom_alias"] is True

        # Second should be auto-generated
        assert results[1]["short_url"] != "https://www.example.com/mixed2"
        assert results[1]["is_custom_alias"] is False

    def test_batch_shorten_empty_array(self):
        """Test batch shortening with empty array"""
        payload = []

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_batch_shorten_single_url(self):
        """Test batch shortening with single Url"""
        payload = [{"long_url": "https://www.example.com/single-batch"}]

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        results = response.data
        assert len(results) == 1

    def test_batch_shorten_invalid_url_in_batch(self):
        """Test batch with one invalid Url"""
        payload = {
            "urls": [
                {"long_url": "https://www.example.com/valid"},
                {"long_url": "not-a-valid-url"},
                {"long_url": "https://www.example.com/also-valid"},
            ]
        }

        response = self.client.post(self.url, payload, format="json")

        # Depending on your implementation:
        # Option 1: Reject entire batch (all-or-nothing)
        # Option 2: Process valid URLs, report errors for invalid ones

        if response.status_code == status.HTTP_400_BAD_REQUEST:
            # All-or-nothing approach
            assert (
                "error" in str(response.data).lower()
                or "invalid" in str(response.data).lower()
            )
        elif (
            response.status_code == status.HTTP_201_CREATED
            or response.status_code == status.HTTP_207_MULTI_STATUS
        ):
            # Partial success approach
            results = (
                response.data.get("urls")
                or response.data.get("results")
                or response.data
            )
            # Should have some indication of which URLs failed
            assert len(results) >= 2  # At least the valid ones

    def test_batch_shorten_duplicate_aliases(self):
        """Test batch with duplicate custom aliases"""
        payload = {
            "urls": [
                {
                    "long_url": "https://www.example.com/dup1",
                    "short_url": "duplicate-alias",
                },
                {
                    "long_url": "https://www.example.com/dup2",
                    "short_url": "duplicate-alias",
                },
            ]
        }

        response = self.client.post(self.url, payload, format="json")

        # Should reject due to duplicate alias
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_207_MULTI_STATUS,  # If partial success is supported
        ]

    def test_batch_shorten_with_expiry_dates(self):
        """Test batch shortening with expiry dates"""
        from datetime import datetime, timedelta
        from django.utils import timezone

        future_date = (timezone.now() + timedelta(days=30)).isoformat()

        payload = [
            {
                "long_url": "https://www.example.com/expiry1",
                "expiry_date": future_date,
            },
            {
                "long_url": "https://www.example.com/expiry2",
                "expiry_date": future_date,
            },
        ]

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        results = response.data

        # Verify expiry dates were set
        for result in results:
            assert result["expiry_date"] is not None

    def test_batch_shorten_large_batch(self):
        """Test batch shortening with many URLs"""
        # Generate 50 URLs
        urls = [
            {"long_url": f"https://www.example.com/large-batch-{i}"} for i in range(50)
        ]

        response = self.client.post(self.url, urls, format="json")

        # Depending on your limits, this might succeed or fail
        if response.status_code == status.HTTP_201_CREATED:
            results = response.data
            assert len(results) == 50
        elif response.status_code == status.HTTP_400_BAD_REQUEST:
            # Batch size limit exceeded
            assert (
                "limit" in str(response.data).lower()
                or "too many" in str(response.data).lower()
            )

    def test_batch_shorten_exceeds_limit(self):
        """Test batch shortening beyond maximum allowed"""
        # Try with 1000 URLs (likely over any reasonable limit)
        urls = [
            {"long_url": f"https://www.example.com/limit-test-{i}"} for i in range(1000)
        ]
        response = self.client.post(self.url, urls, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            "limit" in str(response.data).lower()
            or "too many" in str(response.data).lower()
        )

    def test_batch_shorten_unauthenticated(self):
        """Test batch shortening without authentication"""
        self.client.force_authenticate(user=None)

        payload = [{"long_url": "https://www.example.com/noauth"}]

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_batch_shorten_all_urls_created_in_db(self):
        """Test that all URLs are actually created in database"""
        payload = [
            {"long_url": "https://www.example.com/db-test1"},
            {"long_url": "https://www.example.com/db-test2"},
            {"long_url": "https://www.example.com/db-test3"},
        ]

        initial_count = Url.objects.count()

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        final_count = Url.objects.count()
        assert final_count == initial_count + 3

    def test_batch_shorten_response_structure(self):
        """Test batch response structure is correct"""
        payload = [{"long_url": "https://www.example.com/structure-test"}]

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        # Verify response structure
        assert isinstance(response.data, dict) or isinstance(response.data, list)

        results = response.data

        if isinstance(results, list) and len(results) > 0:
            first_result = results[0]
            assert "short_url" in first_result
            assert "long_url" in first_result
            assert "created_at" in first_result
            assert "user" in first_result


@pytest.mark.django_db
class TestNewFeaturesIntegration:
    """Integration tests combining new features"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        cache.clear()

    def teardown_method(self):
        cache.clear()

    def test_batch_create_then_generate_qr_codes(self):
        """Test creating URLs in batch then generating QR codes for them"""
        # Batch create
        batch_payload = [
            {
                "long_url": "https://www.example.com/qr-batch1",
                "short_url": "qr-batch-1",
            },
            {
                "long_url": "https://www.example.com/qr-batch2",
                "short_url": "qr-batch-2",
            },
        ]

        batch_response = self.client.post(
            "/api/url/batch-shorten/", batch_payload, format="json"
        )
        assert batch_response.status_code == status.HTTP_201_CREATED

        results = batch_response.data

        # Generate QR code for each
        for result in results:
            qr_url = f'/api/url/qr/{result["short_url"]}/'
            qr_response = self.client.get(qr_url)

            assert qr_response.status_code == status.HTTP_200_OK
            assert qr_response["Content-Type"] == "image/png"

    def test_custom_alias_redirect_and_qr_code(self):
        """Test complete workflow: create with custom alias, redirect, and QR code"""
        # Create with custom alias
        create_payload = {
            "long_url": "https://www.example.com/complete-workflow",
            "short_url": "complete-test",
        }
        create_response = self.client.post(
            "/api/url/shorten/", create_payload, format="json"
        )
        assert create_response.status_code == status.HTTP_201_CREATED

        # Test redirect
        redirect_response = self.client.get("/api/url/redirect/complete-test/")
        assert redirect_response.status_code == status.HTTP_302_FOUND


@pytest.mark.django_db
class TestURLShortenWithAutoShortCode:
    """Test POST /api/url/shorten/ endpoint with auto-assigned short codes from pool"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/api/url/shorten/"

        # Pre-populate short code pool
        ShortCodeService().refill_pool(target_size=100)

    def test_shorten_url_auto_assigns_code_from_pool(self):
        """Test URL shortening automatically assigns a code from pool"""
        payload = {"long_url": "https://www.example.com/very/long/url/path"}

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "short_url" in response.data
        assert len(response.data["short_url"]) == 8
        assert response.data["long_url"] == payload["long_url"]
        assert response.data["user"] == self.user.id

    def test_shorten_url_code_removed_from_pool(self):
        """Test that assigned short code is removed from Redis pool"""
        initial_size = ShortCodeService().redis_client.scard(ShortCodeService.POOL_KEY)

        payload = {"long_url": "https://www.example.com/test"}
        response = self.client.post(self.url, payload, format="json")
        assigned_short_url = response.data["short_url"]

        # Verify pool size decreased
        new_size = ShortCodeService().redis_client.scard(ShortCodeService.POOL_KEY)
        assert new_size == initial_size - 1

        # Verify code is not in pool anymore
        assert not ShortCodeService().redis_client.sismember(
            ShortCodeService.POOL_KEY, assigned_short_url
        )

    def test_shorten_multiple_urls_unique_codes(self):
        """Test that multiple URL shortenings get unique codes"""
        short_urls = set()

        for i in range(10):
            payload = {"long_url": f"https://www.example.com/url{i}"}
            response = self.client.post(self.url, payload, format="json")
            assert response.status_code == status.HTTP_201_CREATED
            short_urls.add(response.data["short_url"])

        # All codes should be unique
        assert len(short_urls) == 10

    def test_shorten_url_empty_pool_fallback(self):
        """Test that system generates code on the fly if pool is empty"""
        # Empty the pool
        ShortCodeService().redis_client.delete(ShortCodeService.POOL_KEY)

        payload = {"long_url": "https://www.example.com/test"}
        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "short_url" in response.data
        assert len(response.data["short_url"]) == 8

    def test_shorten_url_saves_to_database(self):
        """Test that shortened URL is saved correctly to database"""
        payload = {"long_url": "https://www.example.com/database-test"}
        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        # Verify in database
        url_obj = Url.objects.get(short_url=response.data["short_url"])
        assert url_obj.long_url == payload["long_url"]
        assert url_obj.user == self.user
        assert url_obj.visits == 0

    def test_shorten_url_unauthenticated(self):
        """Test URL shortening without authentication"""
        self.client.force_authenticate(user=None)
        payload = {"long_url": "https://www.example.com"}

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_shorten_url_invalid_format(self):
        """Test URL shortening with invalid URL format"""
        payload = {"long_url": "not-a-valid-url"}

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_shorten_url_missing_field(self):
        """Test URL shortening without required field"""
        payload = {}

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestShortCodePoolRefill:
    """Test automatic pool refill when hitting threshold"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/api/url/shorten/"

        # Start with a smaller pool for testing
        ShortCodeService.MIN_POOL_SIZE = 50
        ShortCodeService().refill_pool(target_size=50)

    def test_pool_triggers_refill_at_30_percent(self):
        """Test that pool triggers async refill when it hits 30% capacity"""
        with patch.object(ShortCodeService, "refill_pool") as mock_refill:
            # Deplete pool to exactly 30% (15 codes remaining)
            for i in range(35):
                payload = {"long_url": f"https://www.example.com/url{i}"}
                response = self.client.post(self.url, payload, format="json")
                assert response.status_code == status.HTTP_201_CREATED

            # Verify pool size
            current_size = ShortCodeService().redis_client.scard(
                ShortCodeService.POOL_KEY
            )
            assert current_size == 15

            # Next creation should trigger refill
            payload = {"long_url": "https://www.example.com/trigger"}
            response = self.client.post(self.url, payload, format="json")
            assert response.status_code == status.HTTP_201_CREATED

            # Verify async refill was called
            mock_refill.assert_called_once()

    def test_pool_continues_working_during_refill(self):
        """Test that pool continues to work while refilling"""
        # Deplete pool to 30%
        for i in range(35):
            payload = {"long_url": f"https://www.example.com/url{i}"}
            self.client.post(self.url, payload, format="json")

        # Continue creating URLs - should work even if refill is triggered
        for i in range(10):
            payload = {"long_url": f"https://www.example.com/during-refill{i}"}
            response = self.client.post(self.url, payload, format="json")
            assert response.status_code == status.HTTP_201_CREATED

    def test_pool_refill_maintains_minimum_size(self):
        """Test that refill brings pool back to minimum size"""
        # Deplete pool significantly
        for i in range(40):
            payload = {"long_url": f"https://www.example.com/url{i}"}
            self.client.post(self.url, payload, format="json")

        # Manually trigger refill
        ShortCodeService().refill_pool()

        # Verify pool is back to minimum size
        current_size = ShortCodeService().redis_client.scard(ShortCodeService.POOL_KEY)
        assert current_size >= ShortCodeService.MIN_POOL_SIZE

    def test_pool_does_not_duplicate_codes(self):
        """Test that refill doesn't create duplicate codes"""
        initial_size = ShortCodeService().redis_client.scard(ShortCodeService.POOL_KEY)

        # Get all codes from pool
        initial_codes = ShortCodeService().redis_client.smembers(
            ShortCodeService.POOL_KEY
        )

        # Refill pool
        ShortCodeService().refill_pool(target_size=100)

        # Get all codes after refill
        final_codes = ShortCodeService().redis_client.smembers(
            ShortCodeService.POOL_KEY
        )

        # Verify no duplicates (Redis SET naturally prevents this, but good to test)
        assert len(final_codes) == len(set(final_codes))
        assert len(final_codes) >= initial_size

    def test_high_volume_depletes_and_refills(self):
        """Test high volume usage depletes and triggers refill"""
        initial_size = ShortCodeService().redis_client.scard(ShortCodeService.POOL_KEY)

        with patch.object(ShortCodeService, "refill_pool") as mock_refill:
            # Create many short URLs rapidly
            for i in range(40):
                payload = {"long_url": f"https://www.example.com/high-volume{i}"}
                response = self.client.post(self.url, payload, format="json")
                assert response.status_code == status.HTTP_201_CREATED

            # Pool should be significantly depleted
            current_size = ShortCodeService().redis_client.scard(
                ShortCodeService.POOL_KEY
            )
            assert current_size < initial_size
            assert current_size <= initial_size * 0.3

            # Refill should have been triggered
            assert mock_refill.call_count >= 1


@pytest.mark.django_db
class TestShortCodeCollisionResistance:
    """Test collision resistance scenarios"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )

        # Pre-populate short code pool
        ShortCodeService().refill_pool(target_size=100)

    def test_multiple_users_no_collision(self):
        """Test that multiple users get unique codes"""
        client1 = APIClient()
        client1.force_authenticate(user=self.user)

        client2 = APIClient()
        client2.force_authenticate(user=self.other_user)

        url = "/api/url/shorten/"

        # Create URLs for both users simultaneously
        short_urls = set()
        for i in range(5):
            payload1 = {"long_url": f"https://www.example.com/user1-{i}"}
            payload2 = {"long_url": f"https://www.example.com/user2-{i}"}

            response1 = client1.post(url, payload1, format="json")
            response2 = client2.post(url, payload2, format="json")

            assert response1.status_code == status.HTTP_201_CREATED
            assert response2.status_code == status.HTTP_201_CREATED

            short_urls.add(response1.data["short_url"])
            short_urls.add(response2.data["short_url"])

        # All codes should be unique (10 total)
        assert len(short_urls) == 10

    def test_rapid_concurrent_creation_no_collision(self):
        """Test rapid concurrent creation maintains uniqueness"""
        self.client.force_authenticate(user=self.user)

        short_urls = []
        for i in range(20):
            payload = {"long_url": f"https://www.example.com/rapid{i}"}
            response = self.client.post("/api/url/shorten/", payload, format="json")
            assert response.status_code == status.HTTP_201_CREATED
            short_urls.append(response.data["short_url"])

        # All codes should be unique
        assert len(short_urls) == len(set(short_urls))

    def test_database_constraint_prevents_collision(self):
        """Test that database unique constraint prevents duplicate short URLs"""
        self.client.force_authenticate(user=self.user)
        payload = {"long_url": "https://www.example.com/test"}
        response1 = self.client.post("/api/url/shorten/", payload, format="json")
        short_url = response1.data["short_url"]

        # Try to create another URL object with same short_url (should fail at DB level)
        with pytest.raises(Exception):  # IntegrityError expected
            Url.objects.create(
                long_url="https://www.example.com/different",
                short_url=short_url,
                user=self.user,
            )


@pytest.mark.django_db
class TestPoolHealthMonitoring:
    """Test pool health and edge cases"""

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

        ShortCodeService.MIN_POOL_SIZE = 50
        ShortCodeService().refill_pool(target_size=50)

    def test_pool_never_fully_depletes_with_fallback(self):
        """Test that even if pool is empty, system continues to work"""
        # Drain the entire pool
        for i in range(60):
            payload = {"long_url": f"https://www.example.com/drain{i}"}
            self.client.post("/api/url/shorten/", payload, format="json")

        # Should still be able to create URLs (fallback generation)
        payload = {"long_url": "https://www.example.com/after-depletion"}
        response = self.client.post("/api/url/shorten/", payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.data["short_url"]) == 8

    def test_pool_size_check_accuracy(self):
        """Test that pool size checks are accurate"""
        expected_size = 50
        ShortCodeService().refill_pool(target_size=expected_size)

        actual_size = ShortCodeService().redis_client.scard(ShortCodeService.POOL_KEY)
        assert actual_size == expected_size

        # Remove 10 codes
        for i in range(10):
            payload = {"long_url": f"https://www.example.com/test{i}"}
            self.client.post("/api/url/shorten/", payload, format="json")

        actual_size = ShortCodeService().redis_client.scard(ShortCodeService.POOL_KEY)
        assert actual_size == expected_size - 10

    def test_pool_recovery_after_redis_flush(self):
        """Test that pool can recover if Redis is flushed"""
        # Flush Redis (simulating Redis restart or data loss)
        ShortCodeService().redis_client.flushdb()

        # Pool should be empty
        assert ShortCodeService().redis_client.scard(ShortCodeService.POOL_KEY) == 0

        # System should still work with fallback generation
        payload = {"long_url": "https://www.example.com/after-flush"}
        response = self.client.post("/api/url/shorten/", payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        # Can manually refill pool
        ShortCodeService().refill_pool(target_size=50)
        assert ShortCodeService().redis_client.scard(ShortCodeService.POOL_KEY) >= 50
