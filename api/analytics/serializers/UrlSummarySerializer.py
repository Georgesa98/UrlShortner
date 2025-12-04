from rest_framework.serializers import BaseSerializer, DictField

from api.analytics.serializers.VisitSerializer import VisitSerializer


class UrlSummarySerializer(BaseSerializer):
    basic_info = DictField()
    analytics = DictField()
    top_metrics = DictField()
    recent_visitors = VisitSerializer(many=True)

    def to_representation(self, instance):
        response = {}
        response["basic_info"] = instance["basic_info"]
        response["analytics"] = instance["analytics"]
        response["top_metrics"] = instance["top_metrics"]
        response["recent_visitors"] = VisitSerializer(
            instance["recent_visitors"], many=True
        ).data

        return response
