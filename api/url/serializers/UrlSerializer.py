from rest_framework.serializers import (
    ModelSerializer,
    DateTimeField,
    ValidationError,
)
from api.url.models import Url
from api.url.serializers.UrlStatusSerializer import UrlStatusSerializer
from api.url.utils import urlChecker


class UrlSerializer(ModelSerializer):
    expiry_date = DateTimeField(required=False, allow_null=True)
    url_status = UrlStatusSerializer(read_only=True)

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
            "url_status",
            "last_accessed",
            "days_until_expiry",
        ]
        read_only_fields = [
            "short_url",
            "created_at",
            "updated_at",
            "visits",
            "url_status",
            "last_accessed",
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
