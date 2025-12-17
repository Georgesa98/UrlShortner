from .models import RedirectionRule
from api.url.models import Url
from django.contrib.auth import get_user_model

User = get_user_model()


class RedirectionService:
    @staticmethod
    def create_rule(validated_data):
        """Create a new redirection rule with business logic."""

        url = validated_data["url"]
        priority = validated_data.get("priority", 0)
        if RedirectionRule.objects.filter(url=url, priority=priority).exists():
            raise ValueError(f"Priority {priority} already exists for this URL")

        original_url = url.long_url
        target_url = validated_data["target_url"]
        if target_url == original_url:
            raise ValueError("Target URL cannot be the same as the original URL")

        rule = RedirectionRule.objects.create(**validated_data)
        return rule

    @staticmethod
    def get_rules(url_id=None, filters=None, ordering=None):
        """Retrieve redirection rules with flexible filtering."""

        queryset = RedirectionRule.objects.select_related("url")

        if url_id:
            queryset = queryset.filter(url_id=url_id)

        if filters:
            queryset = queryset.filter(**filters)

        ordering = ordering or ["priority", "created_at"]
        return queryset.order_by(*ordering)

    @staticmethod
    def get_rule_by_id(rule_id):
        """Get a single rule by ID."""

        try:
            return RedirectionRule.objects.select_related("url").get(id=rule_id)
        except RedirectionRule.DoesNotExist:
            raise ValueError(f"Redirection rule with ID {rule_id} not found")

    @staticmethod
    def update_rule(rule, validated_data):
        """Update an existing redirection rule."""

        if "priority" in validated_data:
            new_priority = validated_data["priority"]
            if (
                RedirectionRule.objects.filter(url=rule.url, priority=new_priority)
                .exclude(id=rule.id)
                .exists()
            ):
                raise ValueError(f"Priority {new_priority} already exists for this URL")

        if "target_url" in validated_data:
            target_url = validated_data["target_url"]
            if target_url == rule.url.long_url:
                raise ValueError("Target URL cannot be the same as the original URL")

        for attr, value in validated_data.items():
            setattr(rule, attr, value)
        rule.save()
        return rule

    @staticmethod
    def delete_rule(rule):
        """Delete a redirection rule with cleanup logic."""

        rule.delete()

    @staticmethod
    def batch_create_rules(validated_rules_data, user):
        """Bulk create redirection rules - assumes data is pre-validated.

        Args:
            validated_rules_data (list): List of validated rule data dicts
            user: User instance for ownership validation

        Returns:
            list: Created rule instances
        """
        created_rules = []

        for rule_data in validated_rules_data:
            url = rule_data["url"]
            if url.user != user and user.role != User.Role.ADMIN:
                raise ValueError(f"URL {url.id} not owned by user")

            priority = rule_data.get("priority", 0)
            if RedirectionRule.objects.filter(url=url, priority=priority).exists():
                raise ValueError(f"Priority {priority} already exists for this URL")

            rule = RedirectionRule.objects.create(
                url=url,
                name=rule_data.get("name", ""),
                conditions=rule_data.get("conditions", {}),
                target_url=rule_data["target_url"],
                priority=priority,
                is_active=rule_data.get("is_active", True),
            )

            created_rules.append(
                {
                    "id": rule.id,
                    "name": rule.name,
                    "url_id": rule.url.id,
                    "conditions": rule.conditions,
                    "target_url": rule.target_url,
                    "priority": rule.priority,
                    "is_active": rule.is_active,
                    "created_at": rule.created_at.isoformat(),
                }
            )

        return created_rules

    @staticmethod
    def batch_delete_rules(rule_ids, user):
        """Bulk delete redirection rules with validation.

        Args:
            rule_ids (list): List of rule IDs to delete
            user: User instance for ownership validation

        Returns:
            dict: {
                'deleted_count': int,
                'failed_rules': list of {'rule_id': int, 'error': str}
            }
        """
        deleted_count = 0
        failed_rules = []

        for rule_id in rule_ids:
            try:
                rule = RedirectionRule.objects.select_related("url").get(id=rule_id)

                if rule.url.user != user and user.role != User.Role.ADMIN:
                    failed_rules.append(
                        {"rule_id": rule_id, "error": "Rule not owned by user"}
                    )
                    continue

                rule.delete()
                deleted_count += 1

            except RedirectionRule.DoesNotExist:
                failed_rules.append({"rule_id": rule_id, "error": "Rule not found"})
            except Exception as e:
                failed_rules.append({"rule_id": rule_id, "error": str(e)})

        return {"deleted_count": deleted_count, "failed_rules": failed_rules}

    @staticmethod
    def reorder_priorities(url, start_priority=0):
        """Reorder rule priorities for a URL."""

        rules = RedirectionRule.objects.filter(url=url).order_by("priority")
        current_priority = start_priority
        for rule in rules:
            rule.priority = current_priority
            rule.save()
            current_priority += 1

    @staticmethod
    def get_active_rules_for_url(url_id):
        """Get only active rules for rule evaluation."""

        return RedirectionRule.objects.filter(url_id=url_id, is_active=True).order_by(
            "priority"
        )

    def test_evaluate_rules(self, url_id, test_context):
        """Test rule evaluation with provided context, return matched rule or None."""
        try:
            from api.url.models import Url

            Url.objects.get(id=url_id)

            active_rules = self.get_active_rules_for_url(url_id)
            if not active_rules:
                return None

            normalized_context = {
                "country": test_context.get("country"),
                "device_type": test_context.get("device_type"),
                "browser": test_context.get("browser"),
                "os": test_context.get("os"),
                "language": test_context.get("language"),
                "mobile": test_context.get("mobile"),
                "referrer": test_context.get("referrer"),
                "time_range": test_context.get("time_range"),
            }

            matched_rule = self._evaluate_rules(active_rules, normalized_context)
            return matched_rule
        except Url.DoesNotExist:
            raise ValueError(f"URL with ID {url_id} not found")
        except Exception as e:
            raise ValueError(f"Error evaluating rules: {str(e)}")

    def evaluate_redirection_rules(self, request, url_instance):
        """Evaluate active redirection rules for the URL and return redirect URL if match."""
        try:
            active_rules = self.get_active_rules_for_url(url_instance.id)
            if not active_rules:
                return None

            request_context = self._extract_request_context(request)
            matched_rule = self._evaluate_rules(active_rules, request_context)
            return matched_rule
        except Exception:
            return None

    def _extract_request_context(self, request):
        """Extract client context for rule evaluation."""
        from api.analytics.utils import (
            get_ip_address,
            convert_ip_to_location,
            parse_user_agent,
        )
        from datetime import datetime

        ip = get_ip_address(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "")

        # Get country from IP
        country = convert_ip_to_location(ip)
        country = country.upper() if country and country != "Unknown" else None

        # Parse user agent
        ua_data = parse_user_agent(user_agent)

        # Current time for time_range
        current_time = datetime.now().strftime("%H:%M")

        mobile = ua_data.get("is_mobile", False) or ua_data.get(
            "device", ""
        ).lower() in ["iphone", "android", "ipad"]

        return {
            "country": country,
            "device_type": "mobile" if mobile else "desktop",
            "browser": ua_data.get("browser", ""),
            "os": ua_data.get("os", ""),
            "language": self._parse_accept_language(
                request.META.get("HTTP_ACCEPT_LANGUAGE", "")
            ),
            "mobile": mobile,
            "referrer": request.META.get("HTTP_REFERER", ""),
            "time_range": current_time,
        }

    def _parse_accept_language(self, accept_language):
        """Parse Accept-Language header to get primary language."""
        if not accept_language:
            return None
        # Parse "en-US,en;q=0.9" -> "en"
        primary = accept_language.split(",")[0].split("-")[0].split(";")[0].strip()
        return primary.lower()

    def _evaluate_rules(self, rules, context):
        """Evaluate rules in priority order, return first match."""
        for rule in rules:
            if self._rule_matches(rule, context):
                return rule
        return None

    def _rule_matches(self, rule, context):
        """Check if rule conditions match request context."""
        conditions = rule.conditions
        for key, expected_value in conditions.items():
            actual_value = context.get(key)
            if not self._condition_matches(key, expected_value, actual_value):
                return False
        return True

    def _condition_matches(self, key, expected, actual):
        """Check individual condition matching."""
        if actual is None:
            return False

        if key == "country":
            return (
                actual in expected if isinstance(expected, list) else actual == expected
            )
        elif key in ["device_type", "browser", "os"]:
            return actual == expected
        elif key == "mobile":
            return actual == expected
        elif key == "language":
            return (
                actual in expected if isinstance(expected, list) else actual == expected
            )
        elif key == "time_range":
            return self._time_in_range(actual, expected)
        elif key == "referrer":
            return (
                any(pattern in actual for pattern in expected)
                if isinstance(expected, list)
                else expected in actual
            )
        return False

    def _time_in_range(self, current_time, time_range):
        """Check if current_time (HH:MM) is within time_range."""
        if not time_range or "start" not in time_range or "end" not in time_range:
            return False

        start = time_range["start"]
        end = time_range["end"]

        # Handle overnight ranges (e.g., 22:00 to 06:00)
        if start <= end:
            return start <= current_time <= end
        else:
            return current_time >= start or current_time <= end
