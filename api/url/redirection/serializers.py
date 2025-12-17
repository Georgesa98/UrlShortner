import re
from rest_framework import serializers
from iso3166 import countries
from .models import RedirectionRule
from api.url.models import Url


class RedirectionRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RedirectionRule
        fields = [
            "id",
            "name",
            "url",
            "conditions",
            "target_url",
            "priority",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_conditions(self, value):
        """Validate the conditions JSON structure."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Conditions must be a dictionary.")

        allowed_keys = set(RedirectionRule.CONDITION_KEYS)
        for key in value.keys():
            if key not in allowed_keys:
                raise serializers.ValidationError(
                    f"Invalid condition key '{key}'. Allowed keys: {list(allowed_keys)}"
                )

        self._validate_country(value.get("country"))
        self._validate_device_type(value.get("device_type"))
        self._validate_browser(value.get("browser"))
        self._validate_os(value.get("os"))
        self._validate_language(value.get("language"))
        self._validate_mobile(value.get("mobile"))
        self._validate_referrer(value.get("referrer"))
        self._validate_time_range(value.get("time_range"))

        return value

    def _validate_country(self, value):
        if value is not None:
            if not isinstance(value, list):
                raise serializers.ValidationError(
                    {"country": "Must be a list of country codes."}
                )
            for code in value:
                if not isinstance(code, str) or len(code) != 2:
                    raise serializers.ValidationError(
                        {
                            "country": f"'{code}' is not a valid country code (must be 2-letter ISO code)."
                        }
                    )
                try:
                    countries.get(code.upper())
                except KeyError:
                    raise serializers.ValidationError(
                        {
                            "country": f"'{code}' is not a valid ISO 3166-1 alpha-2 country code."
                        }
                    )

    def _validate_device_type(self, value):
        if value is not None:
            valid_types = ["mobile", "desktop", "tablet"]
            if value not in valid_types:
                raise serializers.ValidationError(
                    {"device_type": f"Must be one of: {valid_types}"}
                )

    def _validate_time_range(self, value):
        if value is not None:
            if (
                not isinstance(value, dict)
                or "start" not in value
                or "end" not in value
            ):
                raise serializers.ValidationError(
                    {"time_range": "Must be a dict with 'start' and 'end' keys."}
                )
            time_pattern = re.compile(r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")

            start_time = value.get("start")
            end_time = value.get("end")

            if not isinstance(start_time, str) or not time_pattern.match(start_time):
                raise serializers.ValidationError(
                    {"time_range": "Start time must be in HH:MM format (24-hour)."}
                )

            if not isinstance(end_time, str) or not time_pattern.match(end_time):
                raise serializers.ValidationError(
                    {"time_range": "End time must be in HH:MM format (24-hour)."}
                )

            if start_time >= end_time:
                raise serializers.ValidationError(
                    {"time_range": "End time must be after start time."}
                )

    def _validate_browser(self, value):
        if value is not None:
            valid_browsers = [
                "chrome",
                "firefox",
                "safari",
                "edge",
                "opera",
                "brave",
                "vivaldi",
                "chromium",
                "internet_explorer",
            ]
            if value not in valid_browsers:
                raise serializers.ValidationError(
                    {"browser": f"Must be one of: {valid_browsers}"}
                )

    def _validate_os(self, value):
        if value is not None:
            valid_os = [
                "windows",
                "macos",
                "linux",
                "android",
                "ios",
                "ubuntu",
                "centos",
                "debian",
                "fedora",
            ]
            if value not in valid_os:
                raise serializers.ValidationError({"os": f"Must be one of: {valid_os}"})

    def _validate_language(self, value):
        if value is not None:
            if not isinstance(value, list):
                raise serializers.ValidationError(
                    {"language": "Must be a list of language codes."}
                )
            for lang in value:
                if not isinstance(lang, str) or len(lang) != 2 or not lang.isalpha():
                    raise serializers.ValidationError(
                        {"language": f"'{lang}' is not a valid 2-letter language code."}
                    )

    def _validate_mobile(self, value):
        if value is not None:
            if not isinstance(value, bool):
                raise serializers.ValidationError(
                    {"mobile": "Must be a boolean (true/false)."}
                )

    def _validate_referrer(self, value):
        if value is not None:
            if not isinstance(value, list):
                raise serializers.ValidationError(
                    {"referrer": "Must be a list of referrer patterns."}
                )
            domain_pattern = re.compile(
                r"^(https?://)?([a-zA-Z0-9-]+\.)*[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(/.*)?$"
            )
            for ref in value:
                if not isinstance(ref, str) or not domain_pattern.match(ref):
                    raise serializers.ValidationError(
                        {"referrer": f"'{ref}' is not a valid domain or URL pattern."}
                    )


class BatchCreateRedirectionRuleSerializer(RedirectionRuleSerializer):
    url_id = serializers.IntegerField(write_only=True)

    class Meta(RedirectionRuleSerializer.Meta):
        fields = RedirectionRuleSerializer.Meta.fields + ["url_id"]
        list_serializer_class = serializers.ListSerializer

    def to_internal_value(self, data):
        """Set url field from url_id."""
        url_id = data.get("url_id")
        if url_id is not None:
            data["url"] = url_id
        return super().to_internal_value(data)


class BatchDeleteRedirectionRuleSerializer(serializers.Serializer):
    rule_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        max_length=50,
        help_text="List of rule IDs to delete (max 50)",
    )

    def validate_rule_ids(self, value):
        """Validate rule IDs list."""
        if not value:
            raise serializers.ValidationError("At least one rule ID must be provided")

        if len(set(value)) != len(value):
            raise serializers.ValidationError("Rule IDs must be unique")

        return value


class TestRedirectionSerializer(serializers.Serializer):
    url_id = serializers.IntegerField(
        required=True, help_text="ID of the URL to test rules for"
    )
    country = serializers.CharField(
        max_length=2,
        required=False,
        allow_blank=True,
        help_text="2-letter country code",
    )
    device_type = serializers.ChoiceField(
        choices=["mobile", "desktop", "tablet"], required=False, help_text="Device type"
    )
    browser = serializers.ChoiceField(
        choices=[
            "chrome",
            "firefox",
            "safari",
            "edge",
            "opera",
            "brave",
            "vivaldi",
            "chromium",
            "internet_explorer",
        ],
        required=False,
        help_text="Browser name",
    )
    os = serializers.ChoiceField(
        choices=[
            "windows",
            "macos",
            "linux",
            "android",
            "ios",
            "ubuntu",
            "centos",
            "debian",
            "fedora",
        ],
        required=False,
        help_text="Operating system",
    )
    language = serializers.CharField(
        max_length=2,
        required=False,
        allow_blank=True,
        help_text="2-letter language code",
    )
    mobile = serializers.BooleanField(required=False, help_text="Is mobile device")
    referrer = serializers.URLField(
        required=False, allow_blank=True, help_text="Referrer URL"
    )
    time_range = serializers.CharField(
        required=False, allow_blank=True, help_text="Current time in HH:MM format"
    )

    def validate_country(self, value):
        if value:
            try:
                countries.get(value.upper())
            except KeyError:
                raise serializers.ValidationError(
                    "Invalid ISO 3166-1 alpha-2 country code."
                )
        return value.upper() if value else None

    def validate_time_range(self, value):
        if value:
            time_pattern = re.compile(r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
            if not time_pattern.match(value):
                raise serializers.ValidationError("Must be in HH:MM format (24-hour).")
        return value
