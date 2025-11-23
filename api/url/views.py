from rest_framework.views import Response, status
from rest_framework.generics import GenericAPIView
from api.analytics.utils import get_ip_address
from api.url.models import Url, UrlStatus
from django.shortcuts import redirect
from datetime import datetime, timezone
from api.url.serializers.ShortenerSerializer import (
    ShortenerSerializer,
)
from api.custom_auth.authentication import CookieJWTAuthentication
from rest_framework.permissions import IsAuthenticated

from api.url.service import BurstProtectionService, get_burst_protection_service
from .permissions import IsUrlOwner
from api.analytics.service import AnalyticsService

# Create your views here.


class Shortener(GenericAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.data["user"] = request.user.id
        try:
            serializer = ShortenerSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status.HTTP_201_CREATED)
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
            serializer = ShortenerSerializer(url_instance)
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
            serializer = ShortenerSerializer(
                url_instance, data=request.data, partial=True
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
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
