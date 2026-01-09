from django.shortcuts import render
from rest_framework.views import APIView, Response, status
from config.utils.responses import SuccessResponse, ErrorResponse
from api.analytics.serializers.UrlSummarySerializer import UrlSummarySerializer
from api.analytics.service import AnalyticsService
from api.custom_auth.authentication import CookieJWTAuthentication
from api.throttling import IPRateThrottle, UserRateThrottle
from api.url.models import Url
from api.url.permissions import IsUrlOwner
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from api.url.serializers.UrlSerializer import ResponseUrlSerializer

# Create your views here.


class TopVisitedUrlsView(APIView):
    throttle_classes = [IPRateThrottle, UserRateThrottle]
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            top_urls = AnalyticsService.get_top_visited_urls(request.user.id, 10)
            serializer = ResponseUrlSerializer(top_urls, many=True)
            data = {"top_urls": serializer.data, "count": len(top_urls)}
            return SuccessResponse(
                data=data,
                message="Top visited URLs retrieved successfully",
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return ErrorResponse(
                message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetUrlSummary(APIView):
    throttle_classes = [IPRateThrottle, UserRateThrottle]
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated, IsUrlOwner]

    def get(self, request, url_id):
        range_days = int(request.GET.get("days", 7))
        try:
            url_instance = Url.objects.select_related("url_status", "user").get(
                pk=url_id
            )
            self.check_object_permissions(request, url_instance)
            result = AnalyticsService.get_url_summary(url_instance, range_days)
            serializer = UrlSummarySerializer(result)
            return SuccessResponse(
                data=serializer.data,
                message="URL summary retrieved successfully",
                status=status.HTTP_200_OK,
            )
        except Url.DoesNotExist:
            return ErrorResponse(
                message="URL does not exist", status=status.HTTP_404_NOT_FOUND
            )
