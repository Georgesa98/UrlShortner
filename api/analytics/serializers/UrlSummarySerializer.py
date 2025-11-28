from rest_framework.serializers import Serializer, DictField

from api.analytics.serializers import VisitSerializer


class UrlSummarySerializer(Serializer):
    basic_info = DictField()
    analytics = DictField()
    top_metrics = DictField()
    recent_visitors = VisitSerializer(many=True)
