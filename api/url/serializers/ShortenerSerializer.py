from rest_framework.serializers import (
    ModelSerializer,
    DateTimeField,
    ValidationError,
)
from api.url.models import Url
from api.url.utils import urlChecker


class ShortenerSerializer(ModelSerializer):
    expiry_date = DateTimeField(required=False, allow_null=True)

    class Meta:
        model = Url
        fields = [
            "long_url",
            "user",
            "expiry_date",
            "short_url",
            "created_at",
            "updated_at",
            "visits",
            "last_accessed",
            "is_active",
            "is_expired",
            "days_until_expiry",
        ]
        read_only_fields = [
            "short_url",
            "created_at",
            "updated_at",
            "visits",
            "last_accessed",
            "is_expired",
            "days_until_expiry",
        ]

    def validate(self, attrs):
        raw_data = super().validate(attrs)
        if self.instance is None:
            if urlChecker(raw_data["long_url"]):
                return raw_data
            else:
                raise ValidationError("please enter a valid url")
        return raw_data

    def create(self, validated_data):
        from api.url.service import UrlService

        return UrlService.create_url(validated_data)

    def update(self, instance, validated_data):
        from api.url.service import UrlService

        return UrlService.update_url(instance, validated_data)
