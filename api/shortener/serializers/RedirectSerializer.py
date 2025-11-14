from rest_framework.serializers import ModelSerializer
from api.shortener.models import Url


class RedirectSerializer(ModelSerializer):
    class Meta:
        model = Url
        fields = ["short_url"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        short_url = representation.get("short_url")
        url = Url.objects.get(short_url=short_url)
        return url
