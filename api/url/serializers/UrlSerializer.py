from rest_framework.serializers import (
    ModelSerializer,
    DateTimeField,
    ValidationError,
    ReadOnlyField,
)
from api.url.models import Url
from api.url.serializers.UrlStatusSerializer import UrlStatusSerializer
from api.url.utils import urlChecker


class ShortenUrlSerializer(ModelSerializer):
    expiry_date = DateTimeField(required=False, allow_null=True)

    class Meta:
        model = Url
        fields = [
            "long_url",
            "user",
            "expiry_date",
        ]

    def validate_long_url(self, value):
        if self.instance is None:
            if urlChecker(value):
                return value
            else:
                raise ValidationError(detail="please enter a valid url")
        return value


class ResponseUrlSerializer(ModelSerializer):
    url_status = UrlStatusSerializer(read_only=True)
    days_until_expiry = ReadOnlyField()

    class Meta:
        model = Url
        fields = [
            "id",
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
