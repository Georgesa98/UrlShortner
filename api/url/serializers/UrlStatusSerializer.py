from rest_framework.serializers import ModelSerializer

from api.url.models import UrlStatus


class UrlStatusSerializer(ModelSerializer):
    class Meta:
        model = UrlStatus
        fields = "__all__"
