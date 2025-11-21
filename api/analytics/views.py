from django.shortcuts import render
from rest_framework.views import APIView, Response, status
from api.analytics.service import AnalyticsService

# Create your views here.


class TopVisitedUrlsView(APIView):
    def get(self, request):
        try:
            top_urls = AnalyticsService.get_top_visited_urls(request.user.id, 10)
            return Response({"top_urls": top_urls, "count": len(top_urls)})
        except Exception as e:
            return Response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)
