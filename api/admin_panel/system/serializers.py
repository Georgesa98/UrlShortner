from rest_framework import serializers
from .models import SystemConfiguration
from config.settings import ALLOWED_CONFIGS_SCHEMA
from typing import Union


class SystemConfigurationSerializer(serializers.ModelSerializer):
    key = serializers.CharField(max_length=128)
    value = serializers.CharField()

    class Meta:
        model = SystemConfiguration
        fields = ["key", "value", "description", "updated_at"]
        read_only_fields = ["updated_at"]

    def validate_key(self, value):
        """Validate that the configuration key is allowed."""
        if value not in ALLOWED_CONFIGS_SCHEMA:
            raise serializers.ValidationError(
                f"Configuration key '{value}' is not allowed"
            )
        return value

    def _convert_to_int(self, value: str) -> str:
        """Convert value to integer and return string representation."""
        try:
            return str(int(value))
        except ValueError:
            raise serializers.ValidationError(f"Value must be of type int")

    def _convert_to_bool(self, value: Union[str, bool]) -> str:
        """Convert value to boolean and return string representation."""
        if isinstance(value, str):
            if value.lower() in ["true", "1", "yes", "on"]:
                return "true"
            elif value.lower() in ["false", "0", "no", "off"]:
                return "false"
            else:
                raise serializers.ValidationError(f"Invalid boolean value: {value}")
        else:
            return str(bool(value)).lower()

    def _validate_str_value(self, value: str, key: str) -> str:
        """Validate string values based on specific key requirements."""
        if key in ["rate_limit_ip", "rate_limit_user"]:
            if "/" not in value:
                raise serializers.ValidationError(
                    f"Rate limit value must contain a '/' character (e.g., '100/hour')"
                )
        return value

    def validate_value(self, value):
        """Validate the value based on the expected type for the configuration key."""
        key = self._get_current_key()
        if not key:
            raise serializers.ValidationError("Key is required for validation")
        if key not in ALLOWED_CONFIGS_SCHEMA:
            raise serializers.ValidationError(
                f"Configuration key '{key}' is not allowed"
            )

        expected_type = ALLOWED_CONFIGS_SCHEMA[key]["type"]

        try:
            if expected_type == int:
                return self._convert_to_int(value)
            elif expected_type == bool:
                return self._convert_to_bool(value)
            elif expected_type == str:
                return self._validate_str_value(value, key)
            else:
                return str(value)
        except (ValueError, TypeError) as e:
            raise serializers.ValidationError(
                f"Value must be of type {expected_type.__name__}. Error: {str(e)}"
            )

    def _get_current_key(self) -> str:
        """Get the current key from context or instance."""
        key = self.context.get("key")
        if not key and self.instance:
            key = self.instance.key
        return key

    def _validate_short_code_length(self, value: str) -> None:
        """Validate short code length value."""
        try:
            length = int(value)
            if not (4 <= length <= 128):
                raise serializers.ValidationError(
                    {"value": "Short code length must be between 4 and 128"}
                )
        except ValueError:
            raise serializers.ValidationError(
                {"value": "Short code length must be a valid integer"}
            )

    def _validate_positive_integer(self, value: str, field_name: str) -> None:
        """Validate positive integer values."""
        try:
            num_value = int(value)
            if num_value <= 0:
                raise serializers.ValidationError(
                    {"value": f"{field_name} must be greater than 0"}
                )
        except ValueError:
            raise serializers.ValidationError(
                {"value": f"{field_name} must be a valid integer"}
            )

    def validate(self, attrs):
        """Additional validation for specific configuration values."""
        key = attrs.get("key")
        value = attrs.get("value")

        if not (key and value):
            return attrs

        if key == "short_code_length":
            self._validate_short_code_length(value)
        elif key in ["short_code_pool_size", "max_urls_per_user"]:
            self._validate_positive_integer(value, "Value")
        elif key == "jwt_access_token_minutes":
            self._validate_positive_integer(value, "JWT access token minutes")
        elif key == "url_mapping_cache_timeout":
            self._validate_positive_integer(value, "Cache timeout")

        return attrs
