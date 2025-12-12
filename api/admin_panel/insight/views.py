from rest_framework.generics import GenericAPIView
from rest_framework.views import Response, status
from api.admin_panel.insight.InsightService import InsightService
from api.custom_auth.authentication import CookieJWTAuthentication
from api.throttling import UserRateThrottle, IPRateThrottle
from api.custom_auth.permissions import IsAdmin
from rest_framework.permissions import IsAuthenticated


# Create your views here.
class PlatformStatsView(GenericAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    throttle_classes = [UserRateThrottle, IPRateThrottle]

    def get(self, request):
        time_range = request.query_params.get("time_range")
        stats = InsightService.get_platform_stats(time_range)
        return Response(stats, status=status.HTTP_200_OK)


class GrowthMetricsView(GenericAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    throttle_classes = [UserRateThrottle, IPRateThrottle]

    def get(self, request):
        metrics = InsightService.get_growth_metrics()
        return Response(metrics, status=status.HTTP_200_OK)


class TopPerformersView(GenericAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    throttle_classes = [UserRateThrottle, IPRateThrottle]

    def get(self, request):
        metric = request.GET.get("metric", "clicks")
        limit = int(request.GET.get("limit", 10))

        performers = InsightService.get_top_performers(metric, limit)
        return Response(performers, status=status.HTTP_200_OK)


class PeakTimesView(GenericAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    throttle_classes = [UserRateThrottle, IPRateThrottle]

    def get(self, request):
        peak_times = InsightService.get_peak_times()
        return Response(peak_times, status=status.HTTP_200_OK)


class GeoDistributionView(GenericAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    throttle_classes = [UserRateThrottle, IPRateThrottle]

    def get(self, request):
        geo_data = InsightService.get_geo_distribution()
        return Response(geo_data, status=status.HTTP_200_OK)
