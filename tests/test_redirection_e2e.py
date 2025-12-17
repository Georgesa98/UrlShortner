import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from api.url.models import Url, UrlStatus
from api.url.redirection.models import RedirectionRule

"""
E2E tests for Redirection Rules endpoints
"""

User = get_user_model()


@pytest.mark.django_db
class TestRedirectionRulesListEndpoint:
    """Test GET/POST /api/url/redirection/rules/ endpoint"""

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

        # Create regular user and URLs
        self.regular_user = User.objects.create_user(
            username="regularuser",
            email="regular@example.com",
            password="regularpass123",
            role=User.Role.USER,
        )

        self.url1 = Url.objects.create(
            long_url="https://www.example.com/page1",
            short_url="abc123",
            user=self.regular_user,
        )
        self.url2 = Url.objects.create(
            long_url="https://www.example.com/page2",
            short_url="def456",
            user=self.regular_user,
        )

        self.base_url = "/api/url/redirection/rules/"

    def test_list_rules_empty(self):
        """Test listing rules when none exist"""
        response = self.client.get(self.base_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] == True
        assert response.data["data"] == []
        assert "Redirection rules retrieved successfully" in response.data["message"]

    def test_list_rules_with_data(self):
        """Test listing rules with existing data"""
        # Create some rules
        rule1 = RedirectionRule.objects.create(
            name="Mobile redirect",
            url=self.url1,
            conditions={"device_type": "mobile"},
            target_url="https://mobile.example.com",
            priority=1,
            is_active=True,
        )
        rule2 = RedirectionRule.objects.create(
            name="Country redirect",
            url=self.url2,
            conditions={"country": ["US", "CA"]},
            target_url="https://us.example.com",
            priority=2,
            is_active=True,
        )

        response = self.client.get(self.base_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] == True
        assert len(response.data["data"]) == 2

        # Check ordering by priority (ascending: lower number = higher priority)
        assert response.data["data"][0]["priority"] == 1
        assert response.data["data"][1]["priority"] == 2

    def test_list_rules_filtered_by_url(self):
        """Test filtering rules by url_id"""
        rule1 = RedirectionRule.objects.create(
            name="Rule for URL1",
            url=self.url1,
            conditions={"device_type": "mobile"},
            target_url="https://mobile.example.com",
            priority=1,
        )
        rule2 = RedirectionRule.objects.create(
            name="Rule for URL2",
            url=self.url2,
            conditions={"country": ["US"]},
            target_url="https://us.example.com",
            priority=1,
        )

        response = self.client.get(f"{self.base_url}?url_id={self.url1.id}")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 1
        assert response.data["data"][0]["name"] == "Rule for URL1"

    def test_create_rule_success(self):
        """Test successful rule creation"""
        payload = {
            "name": "Test redirect rule",
            "url": self.url1.id,
            "conditions": {"device_type": "mobile", "country": ["US"]},
            "target_url": "https://mobile.example.com",
            "priority": 5,
            "is_active": True,
        }

        response = self.client.post(self.base_url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"] == True
        assert "Redirection rule created successfully" in response.data["message"]

        data = response.data["data"]
        assert data["name"] == payload["name"]
        assert data["url"] == payload["url"]
        assert data["conditions"] == payload["conditions"]
        assert data["target_url"] == payload["target_url"]
        assert data["priority"] == payload["priority"]
        assert data["is_active"] == payload["is_active"]

        # Verify in database
        rule = RedirectionRule.objects.get(id=data["id"])
        assert rule.name == payload["name"]

    def test_create_rule_validation_error(self):
        """Test rule creation with invalid data"""
        payload = {
            "name": "",  # Invalid: empty name
            "url": self.url1.id,
            "conditions": {"invalid_key": "value"},  # Invalid condition key
            "target_url": "not-a-url",  # Invalid URL
            "priority": 5,
        }

        response = self.client.post(self.base_url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] == False

    def test_create_rule_business_logic_priority_conflict(self):
        """Test priority uniqueness per URL"""
        # Create first rule
        RedirectionRule.objects.create(
            name="First rule",
            url=self.url1,
            conditions={"device_type": "mobile"},
            target_url="https://first.example.com",
            priority=1,
        )

        # Try to create second rule with same priority
        payload = {
            "name": "Second rule",
            "url": self.url1.id,
            "conditions": {"country": ["US"]},
            "target_url": "https://second.example.com",
            "priority": 1,  # Same priority
        }

        response = self.client.post(self.base_url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.data["message"]

    def test_create_rule_business_logic_loop_prevention(self):
        """Test prevention of redirect loops"""
        payload = {
            "name": "Loop rule",
            "url": self.url1.id,
            "conditions": {"device_type": "mobile"},
            "target_url": self.url1.long_url,  # Same as original URL
            "priority": 1,
        }

        response = self.client.post(self.base_url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "cannot be the same" in response.data["message"]

    def test_create_rule_non_admin_access_denied(self):
        """Test that non-admin users cannot create rules"""
        # Create non-admin client
        regular_client = APIClient()
        regular_client.force_authenticate(user=self.regular_user)

        payload = {
            "name": "Test rule",
            "url": self.url1.id,
            "conditions": {"device_type": "mobile"},
            "target_url": "https://example.com",
            "priority": 1,
        }

        response = regular_client.post(self.base_url, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestRedirectionRuleDetailEndpoint:
    """Test GET/PUT/PATCH/DELETE /api/url/redirection/rules/{id}/ endpoint"""

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

        # Create test data
        self.regular_user = User.objects.create_user(
            username="regularuser",
            email="regular@example.com",
            password="regularpass123",
            role=User.Role.USER,
        )

        self.url = Url.objects.create(
            long_url="https://www.example.com/test",
            short_url="test123",
            user=self.regular_user,
        )

        self.rule = RedirectionRule.objects.create(
            name="Test rule",
            url=self.url,
            conditions={"device_type": "mobile"},
            target_url="https://mobile.example.com",
            priority=1,
            is_active=True,
        )

        self.detail_url = f"/api/url/redirection/rules/{self.rule.id}/"

    def test_get_rule_success(self):
        """Test retrieving a single rule"""
        response = self.client.get(self.detail_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] == True
        assert response.data["data"]["id"] == self.rule.id
        assert response.data["data"]["name"] == self.rule.name

    def test_get_rule_not_found(self):
        """Test retrieving non-existent rule"""
        response = self.client.get("/api/url/redirection/rules/99999/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["success"] == False

    def test_update_rule_put_success(self):
        """Test full update of rule"""
        payload = {
            "name": "Updated rule",
            "url": self.url.id,
            "conditions": {"country": ["US", "CA"]},
            "target_url": "https://updated.example.com",
            "priority": 2,
            "is_active": False,
        }

        response = self.client.put(self.detail_url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] == True
        assert response.data["data"]["name"] == "Updated rule"
        assert response.data["data"]["priority"] == 2
        assert response.data["data"]["is_active"] == False

    def test_update_rule_patch_success(self):
        """Test partial update of rule"""
        payload = {
            "name": "Partially updated rule",
            "priority": 3,
        }

        response = self.client.patch(self.detail_url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["name"] == "Partially updated rule"
        assert response.data["data"]["priority"] == 3
        # Other fields should remain unchanged
        assert response.data["data"]["is_active"] == True

    def test_update_rule_validation_error(self):
        """Test update with invalid data"""
        payload = {
            "conditions": {"invalid_condition": "value"},
            "target_url": "invalid-url",
        }

        response = self.client.patch(self.detail_url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_delete_rule_success(self):
        """Test successful rule deletion"""
        response = self.client.delete(self.detail_url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.data["success"] == True

        # Verify deleted from database
        assert not RedirectionRule.objects.filter(id=self.rule.id).exists()

    def test_delete_rule_not_found(self):
        """Test deleting non-existent rule"""
        response = self.client.delete("/api/url/redirection/rules/99999/")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_detail_endpoints_non_admin_access_denied(self):
        """Test that non-admin users cannot access detail endpoints"""
        regular_client = APIClient()
        regular_client.force_authenticate(user=self.regular_user)

        # Test GET
        response = regular_client.get(self.detail_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Test PUT
        response = regular_client.put(self.detail_url, {}, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Test DELETE
        response = regular_client.delete(self.detail_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestRedirectionRulesConditionsValidation:
    """Test conditions validation in redirection rules"""

    def setup_method(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )
        self.client.force_authenticate(user=self.admin_user)

        self.regular_user = User.objects.create_user(
            username="regularuser",
            email="regular@example.com",
            password="regularpass123",
            role=User.Role.USER,
        )

        self.url = Url.objects.create(
            long_url="https://www.example.com/test",
            short_url="test123",
            user=self.regular_user,
        )

        self.base_url = "/api/url/redirection/rules/"

    def test_conditions_country_validation(self):
        """Test country code validation"""
        # Valid country codes
        payload = {
            "name": "Country rule",
            "url": self.url.id,
            "conditions": {"country": ["US", "CA", "GB"]},
            "target_url": "https://example.com",
            "priority": 1,
        }
        response = self.client.post(self.base_url, payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        # Invalid country code
        payload["conditions"] = {"country": ["INVALID"]}
        response = self.client.post(self.base_url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_conditions_device_type_validation(self):
        """Test device type validation"""
        payload = {
            "name": "Device rule",
            "url": self.url.id,
            "conditions": {"device_type": "mobile"},
            "target_url": "https://mobile.example.com",
            "priority": 1,
        }
        response = self.client.post(self.base_url, payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        # Invalid device type
        payload["conditions"] = {"device_type": "invalid_device"}
        response = self.client.post(self.base_url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_conditions_time_range_validation(self):
        """Test time range validation"""
        payload = {
            "name": "Time rule",
            "url": self.url.id,
            "conditions": {"time_range": {"start": "09:00", "end": "17:00"}},
            "target_url": "https://day.example.com",
            "priority": 1,
        }
        response = self.client.post(self.base_url, payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        # Invalid time format
        payload["conditions"] = {"time_range": {"start": "25:00", "end": "17:00"}}
        response = self.client.post(self.base_url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_conditions_invalid_key_validation(self):
        """Test invalid condition key rejection"""
        payload = {
            "name": "Invalid condition",
            "url": self.url.id,
            "conditions": {"invalid_key": "value"},
            "target_url": "https://example.com",
            "priority": 1,
        }
        response = self.client.post(self.base_url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid condition key" in response.data["message"]

    def test_conditions_browser_validation(self):
        """Test browser validation"""
        payload = {
            "name": "Browser rule",
            "url": self.url.id,
            "conditions": {"browser": "chrome"},
            "target_url": "https://chrome.example.com",
            "priority": 1,
        }
        response = self.client.post(self.base_url, payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        # Invalid browser
        payload["conditions"] = {"browser": "unknown_browser"}
        response = self.client.post(self.base_url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_conditions_language_validation(self):
        """Test language code validation"""
        payload = {
            "name": "Language rule",
            "url": self.url.id,
            "conditions": {"language": ["en", "es", "fr"]},
            "target_url": "https://multi.example.com",
            "priority": 1,
        }
        response = self.client.post(self.base_url, payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        # Invalid language code
        payload["conditions"] = {"language": ["invalid"]}
        response = self.client.post(self.base_url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestRedirectionEvaluation:
    """Test actual redirection behavior when users visit short URLs"""

    def setup_method(self):
        self.client = APIClient()
        # Create regular user and URL
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            role=User.Role.USER,
        )

        self.url = Url.objects.create(
            long_url="https://www.example.com/original",
            short_url="testshort",
            user=self.user,
        )

        # Create active status for the URL
        UrlStatus.objects.create(url=self.url, state=UrlStatus.State.ACTIVE)

        self.redirect_url = f"/api/url/redirect/{self.url.short_url}/"

    def test_no_rules_redirect_to_original(self):
        """Test that without rules, redirects to original URL"""
        response = self.client.get(self.redirect_url)

        assert response.status_code == status.HTTP_302_FOUND
        assert response["Location"] == self.url.long_url

    def test_rule_matches_redirect_to_target(self):
        """Test that matching rule redirects to target URL"""
        # Create rule for mobile devices
        RedirectionRule.objects.create(
            name="Mobile redirect",
            url=self.url,
            conditions={"device_type": "mobile"},
            target_url="https://mobile.example.com",
            priority=1,
            is_active=True,
        )

        # Request with mobile user agent
        mobile_ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
        response = self.client.get(self.redirect_url, HTTP_USER_AGENT=mobile_ua)

        assert response.status_code == status.HTTP_302_FOUND
        assert response["Location"] == "https://mobile.example.com"

    def test_rule_not_matches_redirect_to_original(self):
        """Test that non-matching rule redirects to original URL"""
        # Create rule for mobile, but request with desktop UA
        RedirectionRule.objects.create(
            name="Mobile redirect",
            url=self.url,
            conditions={"device_type": "mobile"},
            target_url="https://mobile.example.com",
            priority=1,
            is_active=True,
        )

        desktop_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        response = self.client.get(self.redirect_url, HTTP_USER_AGENT=desktop_ua)

        assert response.status_code == status.HTTP_302_FOUND
        assert response["Location"] == self.url.long_url

    def test_multiple_rules_priority_ordering(self):
        """Test that rules are evaluated by priority (highest first)"""
        # Create two rules: priority 2 (lower) and priority 1 (higher)
        RedirectionRule.objects.create(
            name="High priority",
            url=self.url,
            conditions={"device_type": "mobile"},
            target_url="https://high-priority.example.com",
            priority=1,
            is_active=True,
        )
        RedirectionRule.objects.create(
            name="Low priority",
            url=self.url,
            conditions={"device_type": "mobile"},
            target_url="https://low-priority.example.com",
            priority=2,
            is_active=True,
        )

        mobile_ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
        response = self.client.get(self.redirect_url, HTTP_USER_AGENT=mobile_ua)

        # Should redirect to high priority rule
        assert response.status_code == status.HTTP_302_FOUND
        assert response["Location"] == "https://high-priority.example.com"

    def test_inactive_rule_ignored(self):
        """Test that inactive rules are not evaluated"""
        RedirectionRule.objects.create(
            name="Inactive rule",
            url=self.url,
            conditions={"device_type": "mobile"},
            target_url="https://inactive.example.com",
            priority=1,
            is_active=False,  # Inactive
        )

        mobile_ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
        response = self.client.get(self.redirect_url, HTTP_USER_AGENT=mobile_ua)

        # Should redirect to original since rule is inactive
        assert response.status_code == status.HTTP_302_FOUND
        assert response["Location"] == self.url.long_url

    def test_browser_condition(self):
        """Test browser-based redirection"""
        RedirectionRule.objects.create(
            name="Chrome redirect",
            url=self.url,
            conditions={"browser": "chrome"},
            target_url="https://chrome.example.com",
            priority=1,
            is_active=True,
        )

        chrome_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124"
        response = self.client.get(self.redirect_url, HTTP_USER_AGENT=chrome_ua)

        assert response.status_code == status.HTTP_302_FOUND
        assert response["Location"] == "https://chrome.example.com"

    def test_os_condition(self):
        """Test OS-based redirection"""
        RedirectionRule.objects.create(
            name="Windows redirect",
            url=self.url,
            conditions={"os": "windows"},
            target_url="https://windows.example.com",
            priority=1,
            is_active=True,
        )

        windows_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        response = self.client.get(self.redirect_url, HTTP_USER_AGENT=windows_ua)

        assert response.status_code == status.HTTP_302_FOUND
        assert response["Location"] == "https://windows.example.com"

    def test_language_condition(self):
        """Test language-based redirection"""
        RedirectionRule.objects.create(
            name="English redirect",
            url=self.url,
            conditions={"language": ["en"]},
            target_url="https://en.example.com",
            priority=1,
            is_active=True,
        )

        response = self.client.get(
            self.redirect_url, HTTP_ACCEPT_LANGUAGE="en-US,en;q=0.9"
        )

        assert response.status_code == status.HTTP_302_FOUND
        assert response["Location"] == "https://en.example.com"

    def test_referrer_condition(self):
        """Test referrer-based redirection"""
        RedirectionRule.objects.create(
            name="Google referrer",
            url=self.url,
            conditions={"referrer": ["google.com"]},
            target_url="https://from-google.example.com",
            priority=1,
            is_active=True,
        )

        response = self.client.get(
            self.redirect_url, HTTP_REFERER="https://www.google.com/search"
        )

        assert response.status_code == status.HTTP_302_FOUND
        assert response["Location"] == "https://from-google.example.com"

    def test_mobile_condition(self):
        """Test mobile boolean condition"""
        RedirectionRule.objects.create(
            name="Mobile users",
            url=self.url,
            conditions={"mobile": True},
            target_url="https://mobile.example.com",
            priority=1,
            is_active=True,
        )

        mobile_ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
        response = self.client.get(self.redirect_url, HTTP_USER_AGENT=mobile_ua)

        assert response.status_code == status.HTTP_302_FOUND
        assert response["Location"] == "https://mobile.example.com"


@pytest.mark.django_db
class TestRuleEvaluationEndpoint:
    """Test POST /api/url/redirection/rules/test/ endpoint for rule evaluation without redirection"""

    def setup_method(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )
        self.client.force_authenticate(user=self.admin_user)

        self.regular_user = User.objects.create_user(
            username="regularuser",
            email="regular@example.com",
            password="regularpass123",
            role=User.Role.USER,
        )

        self.url = Url.objects.create(
            long_url="https://www.example.com/test",
            short_url="evaltest",
            user=self.regular_user,
        )
        UrlStatus.objects.create(url=self.url, state=UrlStatus.State.ACTIVE)

        self.evaluate_url = "/api/url/redirection/rules/test/"

    def test_evaluate_no_rules_returns_original_url(self):
        """Test evaluation with no rules returns original URL"""
        payload = {"url_id": self.url.id, "context": {}}
        response = self.client.post(self.evaluate_url, payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] == True
        assert response.data["data"]["target_url"] == self.url.long_url
        assert response.data["data"]["matched_rule"] is None

    def test_evaluate_rule_matches_returns_target_url(self):
        """Test evaluation when a rule matches"""
        rule = RedirectionRule.objects.create(
            name="Mobile eval",
            url=self.url,
            conditions={"device_type": "mobile"},
            target_url="https://mobile.eval.example.com",
            priority=1,
            is_active=True,
        )
        payload = {"url_id": self.url.id, "device_type": "mobile"}
        response = self.client.post(self.evaluate_url, payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["matched_rule"]["id"] == rule.id
        assert (
            response.data["data"]["matched_rule"]["target_url"]
            == "https://mobile.eval.example.com"
        )

    def test_evaluate_no_match_returns_original_url(self):
        """Test evaluation when no rule matches"""
        RedirectionRule.objects.create(
            name="Mobile eval",
            url=self.url,
            conditions={"device_type": "mobile"},
            target_url="https://mobile.eval.example.com",
            priority=1,
            is_active=True,
        )
        payload = {"url_id": self.url.id, "device_type": "desktop"}
        response = self.client.post(self.evaluate_url, payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["target_url"] == self.url.long_url
        assert response.data["data"]["matched_rule"] is None

    def test_evaluate_multiple_rules_priority_ordering(self):
        """Test evaluation respects priority (lowest number = highest priority)"""
        high_priority_rule = RedirectionRule.objects.create(
            name="High priority eval",
            url=self.url,
            conditions={"device_type": "mobile"},
            target_url="https://high.eval.example.com",
            priority=1,
            is_active=True,
        )
        RedirectionRule.objects.create(
            name="Low priority eval",
            url=self.url,
            conditions={"device_type": "mobile"},
            target_url="https://low.eval.example.com",
            priority=2,
            is_active=True,
        )
        payload = {"url_id": self.url.id, "device_type": "mobile"}
        response = self.client.post(self.evaluate_url, payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["matched_rule"]["id"] == high_priority_rule.id
        assert (
            response.data["data"]["matched_rule"]["target_url"]
            == "https://high.eval.example.com"
        )

    def test_evaluate_inactive_rule_ignored(self):
        """Test evaluation ignores inactive rules"""
        RedirectionRule.objects.create(
            name="Inactive eval",
            url=self.url,
            conditions={"device_type": "mobile"},
            target_url="https://inactive.eval.example.com",
            priority=1,
            is_active=False,
        )
        payload = {"url_id": self.url.id, "device_type": "mobile"}
        response = self.client.post(self.evaluate_url, payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["target_url"] == self.url.long_url
        assert response.data["data"]["matched_rule"] is None

    def test_evaluate_conditions_browser(self):
        """Test evaluation with browser condition"""
        rule = RedirectionRule.objects.create(
            name="Chrome eval",
            url=self.url,
            conditions={"browser": "chrome"},
            target_url="https://chrome.eval.example.com",
            priority=1,
            is_active=True,
        )
        payload = {"url_id": self.url.id, "browser": "chrome"}
        response = self.client.post(self.evaluate_url, payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["matched_rule"]["id"] == rule.id
        assert (
            response.data["data"]["matched_rule"]["target_url"]
            == "https://chrome.eval.example.com"
        )

    def test_evaluate_invalid_url_id(self):
        """Test evaluation with non-existent URL ID"""
        payload = {"url_id": 999999}
        response = self.client.post(self.evaluate_url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] == False

    def test_evaluate_non_admin_access_denied(self):
        """Test that non-admin users cannot access evaluation endpoint"""
        regular_client = APIClient()
        regular_client.force_authenticate(user=self.regular_user)
        payload = {"url_id": self.url.id}
        response = regular_client.post(self.evaluate_url, payload, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_evaluate_payload_validation_error(self):
        """Test evaluation with invalid payload (missing fields)"""
        payload = {}  # Missing url_id
        response = self.client.post(self.evaluate_url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] == False
