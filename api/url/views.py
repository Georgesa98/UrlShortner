from rest_framework.views import Response, status
from rest_framework.generics import GenericAPIView
from api.analytics.utils import get_ip_address
from api.url.models import Url, UrlStatus
from django.shortcuts import redirect
from api.url.serializers.UrlSerializer import (
    UrlSerializer,
)
from api.custom_auth.authentication import CookieJWTAuthentication
from rest_framework.permissions import IsAuthenticated

from api.url.service import (
    UrlService,
    get_burst_protection_service,
)
from .permissions import IsUrlOwner
from api.analytics.service import AnalyticsService

# Create your views here.


class Shortener(GenericAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.data["user"] = request.user.id
        try:
            serializer = UrlSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                UrlService.create_url(serializer.data)
                return Response(serializer.data, status.HTTP_201_CREATED)
        except Exception as e:
            return Response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)


class BatchShorten(GenericAPIView):
    def post(self, request):
        try:
            serializer = UrlSerializer(request.data, many=True)
            if serializer.is_valid(raise_exception=True):
                data = UrlService.batch_shorten(serializer.data)
                return Response(data, status.HTTP_201_CREATED)
        except Exception as e:
            return Response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)


class SpecificUrl(GenericAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated, IsUrlOwner]

    def get_object(self, short_url):
        try:
            return Url.objects.get(short_url=short_url)
        except Url.DoesNotExist:
            return None

    def get(self, request, short_url):
        try:
            url_instance = self.get_object(short_url)
            if url_instance is None:
                return Response(
                    {"error": "URL not found"}, status=status.HTTP_404_NOT_FOUND
                )
            self.check_object_permissions(request, url_instance)
            serializer = UrlSerializer(url_instance)
            return Response(serializer.data, status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status.HTTP_404_NOT_FOUND)

    def patch(self, request, short_url):
        try:
            url_instance = self.get_object(short_url)
            if url_instance is None:
                return Response(
                    {"error": "URL not found"}, status=status.HTTP_404_NOT_FOUND
                )
            self.check_object_permissions(request, url_instance)
            serializer = UrlSerializer(url_instance, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                UrlService.update_url(url_instance, serializer.data)
                return Response(serializer.data, status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, short_url):
        try:
            url_instance = self.get_object(short_url)
            if url_instance is None:
                return Response(
                    {"error": "URL not found"}, status=status.HTTP_404_NOT_FOUND
                )
            self.check_object_permissions(request, url_instance)
            url_instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListUrlsView(GenericAPIView):
    def get(self, request):
        limit = int(request.GET.get("limit", 10))
        page = int(request.GET.get("page", 1))
        url_status = request.GET.get("url_status")
        user_id = request.user.id
        try:
            result = UrlService.fetch_urls_with_filter_and_pagination(
                limit, page, url_status, user_id
            )
            serializer = UrlSerializer(result.object_list, many=True)
            return Response(
                {
                    "urls": serializer.data,
                    "pagination": {
                        "total": result.paginator.count,
                        "page": result.number,
                        "limit": limit,
                        "total_pages": result.paginator.num_pages,
                        "has_next": result.has_next(),
                        "has_previous": result.has_previous(),
                    },
                }
            )
        except Exception as e:
            return Response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)


class Redirect(GenericAPIView):
    def __init__(self, **kwargs):
        self.protection_service = get_burst_protection_service()
        super().__init__(**kwargs)

    def get(self, request, short_url):
        analytic_service = AnalyticsService()
        try:
            ip = get_ip_address(request)
            is_safe = self.protection_service.check_burst(ip, short_url)
            if not is_safe:
                return Response(
                    {"error": "too many requests on this url"},
                    status.HTTP_429_TOO_MANY_REQUESTS,
                )
            url_instance = Url.objects.get(short_url=short_url)
            url_status = UrlStatus.objects.get(url=url_instance)
            if not url_status.state == url_status.State.ACTIVE:
                return Response(
                    {"error": "URL is inactive or expired"},
                    status=status.HTTP_410_GONE,
                )

            analytic_service.record_visit(request, url_instance)
            return redirect(url_instance.long_url)
        except Exception as e:
            return Response(str(e), status.HTTP_404_NOT_FOUND)
