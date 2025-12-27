from rest_framework import serializers
from api.url.models import Url, UrlStatus


class HealthCheckRequestSerializer(serializers.Serializer):
    """
    Serializer for health check request
    """

    url_ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False, required=True
    )


class HealthCheckResultSerializer(serializers.Serializer):
    """
    Serializer for health check result
    """

    status = serializers.CharField()
    url_id = serializers.IntegerField()
    destination = serializers.CharField()
    error = serializers.CharField(required=False, allow_null=True)
