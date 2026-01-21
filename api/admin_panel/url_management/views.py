from rest_framework.views import APIView
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from api.custom_auth.authentication import CookieJWTAuthentication
from api.throttling import IPRateThrottle, UserRateThrottle
from api.admin_panel.url_management.UrlManagementService import UrlManagementService
from api.url.serializers.UrlStatusSerializer import UrlStatusSerializer
from api.url.serializers.UrlSerializer import ResponseUrlSerializer
from api.custom_auth.permissions import IsAdminOrStaff
from api.url.models import Url
from config.utils.responses import SuccessResponse, ErrorResponse
from api.analytics.serializers.VisitSerializer import VisitSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


# Create your views here.
class GetUserUrlsView(GenericAPIView):
    throttle_classes = [IPRateThrottle, UserRateThrottle]
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdminOrStaff, IsAuthenticated]

    def get(self, request, user_id):
        try:
            limit = int(request.GET.get("limit", 10))
            page = int(request.GET.get("page", 1))

            result = UrlManagementService.get_user_urls_with_pagination(
                user_id, limit, page
            )
            serializer = ResponseUrlSerializer(result["urls"], many=True)

            response_data = {
                "urls": serializer.data,
                "pagination": result["pagination"],
            }
            return SuccessResponse(
                data=response_data,
                message="User URLs retrieved successfully",
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return ErrorResponse(
                message="User not found", status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return ErrorResponse(
                message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ListUrlsView(GenericAPIView):
    throttle_classes = [IPRateThrottle, UserRateThrottle]
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdminOrStaff]

    def get(self, request):
        limit = int(request.GET.get("limit", 10))
        page = int(request.GET.get("page", 1))
        query = request.GET.get("query")
        url_status = request.GET.get("url_status")
        date_order = request.GET.get("date_order")
        try:
            result = UrlManagementService.list_urls(
                limit, page, url_status, date_order, query
            )
            serializer = ResponseUrlSerializer(result["urls"], many=True)
            response_data = {
                "urls": serializer.data,
                "pagination": result["pagination"],
            }
            return SuccessResponse(
                data=response_data,
                message="URLs listed successfully",
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return ErrorResponse(
                message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BulkUrlDeletionView(APIView):
    throttle_classes = [IPRateThrottle, UserRateThrottle]
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdminOrStaff]

    def post(self, request):
        try:
            url_ids = request.data.get("url_ids", [])
            if not url_ids:
                return ErrorResponse(
                    message="url_ids list is required",
                    status=status.HTTP_400_BAD_REQUEST,
                )

            deleted_count = UrlManagementService.bulk_url_deletion(url_ids)
            return SuccessResponse(
                data={"deleted_count": deleted_count},
                message="URLs deleted successfully",
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return ErrorResponse(
                message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BulkFlagUrlView(APIView):
    throttle_classes = [IPRateThrottle, UserRateThrottle]
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdminOrStaff]

    def post(self, request):
        try:
            data = request.data.get("data", [])
            if not data:
                return ErrorResponse(
                    message="data list with url_id and state is required",
                    status=status.HTTP_400_BAD_REQUEST,
                )

            result = UrlManagementService.bulk_flag_url(data)
            return SuccessResponse(
                data=result,
                message="URLs flagged successfully",
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return ErrorResponse(
                message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetUrlsStatsView(APIView):
    throttle_classes = [IPRateThrottle, UserRateThrottle]
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdminOrStaff]

    def get(self, request):
        try:
            result = UrlManagementService.urls_stats()
            return SuccessResponse(
                data=result,
                message="URLs stats retrieved successfully",
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return ErrorResponse(
                message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetUrlDetailsView(APIView):
    throttle_classes = [IPRateThrottle, UserRateThrottle]
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdminOrStaff]

    def get(self, request, url_id):
        try:
            result = UrlManagementService.get_url_details(url_id)
            url_serializer = ResponseUrlSerializer(result["url"])
            status_serializer = UrlStatusSerializer(result["url_status"])
            recent_clicks_serializer = VisitSerializer(
                result["recent_clicks"], many=True
            )

            response_data = {
                "url": url_serializer.data,
                "url_status": status_serializer.data,
                "recent_clicks": recent_clicks_serializer.data,
            }
            return SuccessResponse(
                data=response_data,
                message="URL details retrieved successfully",
                status=status.HTTP_200_OK,
            )
        except Url.DoesNotExist:
            return ErrorResponse(
                message="URL not found", status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return ErrorResponse(
                message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdateUrlDestinationView(APIView):
    throttle_classes = [IPRateThrottle, UserRateThrottle]
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdminOrStaff]

    def patch(self, request, short_url):
        try:
            new_destination = request.data.get("new_destination", "")
            if not new_destination:
                return ErrorResponse(
                    message="new_destination is required",
                    status=status.HTTP_400_BAD_REQUEST,
                )

            updated_url = UrlManagementService.updated_url_destination(
                short_url, new_destination
            )
            serializer = ResponseUrlSerializer(updated_url)
            return SuccessResponse(
                data=serializer.data,
                message="URL destination updated successfully",
                status=status.HTTP_200_OK,
            )
        except Url.DoesNotExist:
            return ErrorResponse(
                message="URL not found", status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return ErrorResponse(
                message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
