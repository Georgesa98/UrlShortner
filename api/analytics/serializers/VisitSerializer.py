from rest_framework.serializers import ModelSerializer

from api.analytics.models import Visit


class VisitSerializer(ModelSerializer):
    class Meta:
        model = Visit
        fields = "__all__"
