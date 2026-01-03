from django.http import HttpResponse
from rest_framework.views import Response, status
from rest_framework.generics import GenericAPIView
from config.utils.responses import SuccessResponse, ErrorResponse
from api.analytics.utils import get_ip_address
from api.throttling import IPRateThrottle, UserRateThrottle
from api.url.models import Url, UrlStatus
from django.shortcuts import redirect
from api.url.serializers.UrlSerializer import (
    ResponseUrlSerializer,
    ShortenUrlSerializer,
)
from api.custom_auth.authentication import CookieJWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ValidationError
from rest_framework.exceptions import PermissionDenied
from api.url.services.BurstProtectionService import BurstProtectionService
from api.url.services.UrlService import (
    UrlService,
)
from api.url.utils import generate_qrcode
from .permissions import IsUrlOwner
from api.analytics.service import AnalyticsService
from .redirection.RedirectionService import RedirectionService

# Create your views here.


class Shortener(GenericAPIView):
    throttle_classes = [IPRateThrottle, UserRateThrottle]
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.data["user"] = request.user.id
        try:
            shorten_serializer = ShortenUrlSerializer(data=request.data)
            if shorten_serializer.is_valid(raise_exception=True):
                url_instance = UrlService.create_url(shorten_serializer.data)
                response_serializer = ResponseUrlSerializer(url_instance)
                return SuccessResponse(
                    data=response_serializer.data,
                    message="URL shortened successfully",
                    status=status.HTTP_201_CREATED,
                )
        except ValidationError as e:
            return ErrorResponse(message=str(e), status=status.HTTP_400_BAD_REQUEST)


class BatchShorten(GenericAPIView):
    throttle_classes = [IPRateThrottle, UserRateThrottle]
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            if not request.data or not isinstance(request.data, list):
                raise ValidationError(detail="Input data must be a non-empty list.")
            if len(request.data) > 500:
                raise ValidationError(
                    detail="limit exceeded only 500 url allowed at a time"
                )
            user_id = request.user.id
            serializer = ShortenUrlSerializer(data=request.data, many=True)
            if serializer.is_valid(raise_exception=True):
                data = UrlService.batch_shorten(serializer.data, user_id)
                response_serializer = ResponseUrlSerializer(data, many=True)
                return SuccessResponse(
                    data=response_serializer.data,
                    message="URLs shortened successfully",
                    status=status.HTTP_201_CREATED,
                )
        except ValidationError as e:
            return ErrorResponse(message=str(e), status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return ErrorResponse(
                message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SpecificUrl(GenericAPIView):
    throttle_classes = [IPRateThrottle, UserRateThrottle]
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated, IsUrlOwner]

    def get_object(self, short_url):
        try:
            return Url.objects.select_related("url_status", "user").get(
                short_url=short_url
            )
        except Url.DoesNotExist:
            return None

    def get(self, request, short_url):
        try:
            url_instance = self.get_object(short_url)
            if url_instance is None:
                return ErrorResponse(
                    message="URL not found", status=status.HTTP_404_NOT_FOUND
                )
            self.check_object_permissions(request, url_instance)
            serializer = ResponseUrlSerializer(url_instance)
            return SuccessResponse(
                data=serializer.data,
                message="URL retrieved successfully",
                status=status.HTTP_200_OK,
            )
        except PermissionDenied as e:
            return ErrorResponse(message=str(e), status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return ErrorResponse(message=str(e), status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, short_url):
        try:
            url_instance = self.get_object(short_url)
            if url_instance is None:
                return ErrorResponse(
                    message="URL not found", status=status.HTTP_404_NOT_FOUND
                )
            self.check_object_permissions(request, url_instance)
            serializer = ShortenUrlSerializer(
                instance=url_instance, data=request.data, partial=True
            )

            if serializer.is_valid(raise_exception=True):
                UrlService.update_url(url_instance, serializer.validated_data)
                url_instance.refresh_from_db()
                response_serializer = ResponseUrlSerializer(url_instance)
                return SuccessResponse(
                    data=response_serializer.data,
                    message="URL updated successfully",
                    status=status.HTTP_200_OK,
                )
        except PermissionDenied as e:
            return ErrorResponse(message=str(e), status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return ErrorResponse(
                message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, short_url):
        try:
            url_instance = self.get_object(short_url)
            if url_instance is None:
                return ErrorResponse(
                    message="URL not found", status=status.HTTP_404_NOT_FOUND
                )
            self.check_object_permissions(request, url_instance)
            url_instance.delete()
            return SuccessResponse(
                message="URL deleted successfully", status=status.HTTP_204_NO_CONTENT
            )
        except PermissionDenied as e:
            return ErrorResponse(message=str(e), status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return ErrorResponse(
                message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ListUrlsView(GenericAPIView):
    throttle_classes = [IPRateThrottle, UserRateThrottle]
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit = int(request.GET.get("limit", 10))
        page = int(request.GET.get("page", 1))
        url_status = request.GET.get("url_status")
        user_id = request.user.id
        try:
            result = UrlService.fetch_urls_with_filter_and_pagination(
                limit, page, url_status, user_id
            )
            serializer = ResponseUrlSerializer(result.object_list, many=True)
            data = {
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
            return SuccessResponse(
                data=data,
                message="URLs fetched successfully",
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return ErrorResponse(
                message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class Redirect(GenericAPIView):
    def __init__(self, **kwargs):
        self.protection_service = BurstProtectionService()
        self.service = RedirectionService()
        super().__init__(**kwargs)

    def get(self, request, short_url):
        analytic_service = AnalyticsService()
        try:
            ip = get_ip_address(request)
            is_safe = self.protection_service.check_burst(ip, short_url)
            if not is_safe:
                return ErrorResponse(
                    message="Too many requests on this URL",
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )
            url_instance = Url.objects.select_related("url_status").get(
                short_url=short_url
            )
            if url_instance.url_status.state == url_instance.url_status.State.EXPIRED:
                return ErrorResponse(
                    message="URL is inactive or expired", status=status.HTTP_410_GONE
                )

            matched_rule = self.service.evaluate_redirection_rules(
                request, url_instance
            )
            if matched_rule:
                analytic_service.record_visit(request, url_instance)
                return redirect(matched_rule.target_url)
            else:
                analytic_service.record_visit(request, url_instance)
                return redirect(url_instance.long_url)
        except Exception as e:
            return ErrorResponse(message=str(e), status=status.HTTP_404_NOT_FOUND)


class GenerateQrcode(GenericAPIView):
    throttle_classes = [IPRateThrottle, UserRateThrottle]
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated, IsUrlOwner]

    def get(self, request, short_url):
        try:
            url_instance = Url.objects.select_related("url_status", "user").get(
                short_url=short_url
            )
            self.check_object_permissions(request, url_instance)
            qr_image = generate_qrcode(url_instance.short_url)
            response = HttpResponse(qr_image, "image/png", 200)
            return response
        except PermissionDenied as e:
            return ErrorResponse(message=str(e), status=status.HTTP_403_FORBIDDEN)
        except Url.DoesNotExist as e:
            return ErrorResponse(message=str(e), status=status.HTTP_404_NOT_FOUND)
