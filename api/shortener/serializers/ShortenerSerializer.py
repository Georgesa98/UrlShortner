from rest_framework.serializers import (
    ModelSerializer,
    DateTimeField,
    CharField,
    ValidationError,
)
from api.shortener.models import Url
import secrets
import urllib.parse


class CreateShortenerSerializer(ModelSerializer):
    expiry_date = DateTimeField(required=False, allow_null=True)

    class Meta:
        model = Url
        fields = ["long_url", "expiry_date"]
        read_only_fields = [
            "short_url",
            "created_at",
            "updated_at",
            "access_count",
            "last_accessed",
            "is_active",
        ]

    def generator():
        token = secrets.token_bytes(4)
        return token.hex()

    def urlChecker(url):
        try:
            urllib.parse.urlparse(url)
            return True
        except:
            return False

    def validate(self, attrs):
        raw_data = super().validate(attrs)
        if self.urlChecker(raw_data["long_url"]):
            return raw_data
        else:
            raise ValidationError("please enter a valid url")

    def create(self, validated_data):
        short_url = self.generator()
        url_instance = Url.objects.create(
            long_url=validated_data["long_url"],
            short_url=short_url,
            expiry_date=validated_data("expiry_date"),
        )
        return url_instance
