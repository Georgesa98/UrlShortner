from rest_framework.serializers import (
    ModelSerializer,
    DateTimeField,
    ValidationError,
)
from api.url.models import Url
import secrets
import urllib.parse
from datetime import datetime


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
            "access_count",
            "last_accessed",
            "is_active",
        ]
        read_only_fields = [
            "short_url",
            "created_at",
            "updated_at",
            "access_count",
            "last_accessed",
        ]

    def generator(self):
        token = secrets.token_bytes(4)
        return token.hex()

    def urlChecker(self, url):
        try:
            urllib.parse.urlparse(url)
            return True
        except:
            return False

    def validate(self, attrs):
        raw_data = super().validate(attrs)
        if self.instance is None:
            if self.urlChecker(raw_data["long_url"]):
                return raw_data
            else:
                raise ValidationError("please enter a valid url")
        return raw_data

    def create(self, validated_data):
        short_url = self.generator()
        url_instance = Url.objects.create(
            user=validated_data["user"],
            long_url=validated_data["long_url"],
            short_url=short_url,
            expiry_date=(
                validated_data["expiry_date"]
                if "expiry_date" in validated_data
                else None
            ),
        )
        return url_instance

    def update(self, instance, validated_data):
        instance.long_url = validated_data.get(
            "long_url", validated_data.get("long_url", instance.long_url)
        )
        instance.expiry_date = validated_data.get(
            "expiry_date", validated_data.get("expiry_date", instance.expiry_date)
        )
        instance.is_active = validated_data.get("is_active", instance.is_active)
        instance.updated_at = datetime.now()
        instance.save()
        return instance
