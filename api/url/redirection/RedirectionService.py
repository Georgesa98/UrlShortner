from .models import RedirectionRule


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
            # Fail gracefully - return None for default redirect
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
