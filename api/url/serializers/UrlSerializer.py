from rest_framework.serializers import (
    ModelSerializer,
    DateTimeField,
    CharField,
    ValidationError,
    ReadOnlyField,
)
import re
from api.url.models import Url
from api.url.serializers.UrlStatusSerializer import UrlStatusSerializer
from api.url.utils import urlChecker


class ShortenUrlSerializer(ModelSerializer):
    expiry_date = DateTimeField(required=False, allow_null=True)
    short_url = CharField(required=False, allow_null=True, max_length=64, min_length=8)
    long_url = CharField(required=True)
    name = CharField(required=True)

    class Meta:
        model = Url
        fields = [
            "name",
            "long_url",
            "short_url",
            "user",
            "expiry_date",
        ]

    def validate_short_url(self, value):
        if value is None:
            return True
        if Url.objects.filter(short_url=value).exists():
            raise ValidationError(detail="custom alias already in use")
        VALID_ALIAS_REGEX = re.compile(r"^[a-zA-Z0-9_-]+$")
        if not VALID_ALIAS_REGEX.match(value):
            raise ValidationError(
                detail="custom alias can only contain letters, numbers, hyphens, and underscores"
            )
        return value

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
            "name",
            "user",
            "expiry_date",
            "short_url",
            "is_custom_alias",
            "created_at",
            "updated_at",
            "visits",
            "url_status",
            "last_accessed",
            "days_until_expiry",
        ]
