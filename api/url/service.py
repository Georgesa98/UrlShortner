from api.url.models import Url, UrlStatus
from api.url.utils import generator
from datetime import datetime, timezone


class UrlService:
    @classmethod
    def create_url(self, validated_data: dict):

        short_url = generator()
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
        UrlStatus.objects.create(url=url_instance)
        return url_instance

    @classmethod
    def update_url(self, instance, validated_data):
        instance.long_url = validated_data.get(
            "long_url", validated_data.get("long_url", instance.long_url)
        )

        instance.expiry_date = validated_data.get(
            "expiry_date", validated_data.get("expiry_date", instance.expiry_date)
        )
        instance.is_active = validated_data.get("is_active", instance.is_active)
        instance.updated_at = datetime.now(timezone.utc)
        instance.save()
        return instance
