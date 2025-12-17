from rest_framework import serializers


class FraudOverviewSerializer(serializers.Serializer):
    period_days = serializers.IntegerField()
    total_incidents = serializers.IntegerField()
    incidents_by_type = serializers.ListField(child=serializers.DictField())
    flagged_urls = serializers.IntegerField()
    risk_score = serializers.CharField()
    top_incident_types = serializers.ListField(child=serializers.CharField())
