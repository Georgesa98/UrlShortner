from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from config.utils.responses import SuccessResponse, ErrorResponse
from api.admin_panel.fraud.FraudService import FraudService
from api.admin_panel.fraud.serializers import FraudOverviewSerializer
from api.throttling import IPRateThrottle, UserRateThrottle
from rest_framework.permissions import IsAuthenticated
from api.custom_auth.permissions import IsAdmin


class FraudOverviewView(APIView):
    throttle_classes = [IPRateThrottle, UserRateThrottle]
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        try:
            days_str = request.GET.get("days", "7")
            days = int(days_str) if days_str.isdigit() else 7
        except (ValueError, TypeError):
            days = 7
        try:
            metrics = FraudService.get_overview_metrics(days)
            serializer = FraudOverviewSerializer(metrics)
            return SuccessResponse(
                data=serializer.data,
                message="Fraud overview retrieved successfully",
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return ErrorResponse(
                message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
