from rest_framework.views import APIView, Response, status
from rest_framework.generics import GenericAPIView
from api.admin_panel.services.UrlManagementService import UrlManagementService
from api.admin_panel.services.UserManagementService import UserManagementService
from api.custom_auth.permissions import IsAdminOrStaff
from api.url.serializers.UrlStatusSerializer import UrlStatusSerializer
from api.url.serializers.UrlSerializer import ResponseUrlSerializer
from api.analytics.serializers.VisitSerializer import VisitSerializer
from django.contrib.auth import get_user_model
from api.url.models import Url
from api.analytics.models import Visit
from api.url.serializers.UrlSerializer import (
    ResponseUrlSerializer,
    ShortenUrlSerializer,
)
from api.custom_auth.authentication import CookieJWTAuthentication
from api.throttling import IPRateThrottle, UserRateThrottle
from rest_framework.permissions import IsAuthenticated
from api.url.models import UrlStatus
from django.core.paginator import Paginator
from typing import Dict, Any

User = get_user_model()


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
            return Response(response_data)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BulkUrlDeletionView(APIView):

    throttle_classes = [IPRateThrottle, UserRateThrottle]
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdminOrStaff]

    def post(self, request):
        try:
            url_ids = request.data.get("url_ids", [])
            if not url_ids:
                return Response(
                    {"error": "url_ids list is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            deleted_count = UrlManagementService.bulk_url_deletion(url_ids)
            return Response({"deleted_count": deleted_count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BulkFlagUrlView(APIView):

    throttle_classes = [IPRateThrottle, UserRateThrottle]
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdminOrStaff]

    def post(self, request):
        try:
            data = request.data.get("data", [])
            if not data:
                return Response(
                    {"error": "data list with url_id and state is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            result = UrlManagementService.bulk_flag_url(data)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
            return Response(response_data, status=status.HTTP_200_OK)
        except Url.DoesNotExist:
            return Response(
                {"error": "URL not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SearchUrlsView(GenericAPIView):

    throttle_classes = [IPRateThrottle, UserRateThrottle]
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdminOrStaff]

    def get(self, request):
        try:
            query = request.GET.get("q", "")
            if not query:
                return Response(
                    {"error": "Query parameter 'q' is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            limit = int(request.GET.get("limit", 10))
            page = int(request.GET.get("page", 1))

            result = UrlManagementService.search_urls_with_pagination(
                query, limit, page
            )
            serializer = ResponseUrlSerializer(result["urls"], many=True)

            response_data = {
                "urls": serializer.data,
                "pagination": result["pagination"],
            }
            return Response(response_data)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdateUrlDestinationView(APIView):

    throttle_classes = [IPRateThrottle, UserRateThrottle]
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdminOrStaff]

    def patch(self, request, short_url):
        try:
            new_destination = request.data.get("new_destination", "")
            if not new_destination:
                return Response(
                    {"error": "new_destination is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            updated_url = UrlManagementService.updated_url_destination(
                short_url, new_destination
            )
            serializer = ResponseUrlSerializer(updated_url)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Url.DoesNotExist:
            return Response(
                {"error": "URL not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetUsersView(GenericAPIView):

    throttle_classes = [IPRateThrottle, UserRateThrottle]
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdminOrStaff]

    def get(self, request):
        try:
            roles_param = request.GET.get("roles", "")
            is_active_param = request.GET.get("is_active", "")
            order_by = request.GET.get("order_by", "-date_joined")

            roles = None
            if roles_param:
                roles = [role.strip() for role in roles_param.split(",")]

            is_active = None
            if is_active_param:
                if is_active_param.lower() == "true":
                    is_active = [True]
                elif is_active_param.lower() == "false":
                    is_active = [False]
                else:
                    is_active = [True, False]

            limit = int(request.GET.get("limit", 10))
            page = int(request.GET.get("page", 1))

            result = UserManagementService.get_users_with_pagination(
                roles=roles or [User.Role.USER, User.Role.STAFF, User.Role.ADMIN],
                is_active=is_active or [True, False],
                order_by=order_by,
                limit=limit,
                page=page,
            )

            return Response(result)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ToggleBanUserView(APIView):

    throttle_classes = [IPRateThrottle, UserRateThrottle]
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdminOrStaff]

    def patch(self, request, user_id):
        try:
            user_instance = UserManagementService.toggle_ban_user(user_id)
            user_data = {
                "id": user_instance.id,
                "username": user_instance.username,
                "email": user_instance.email,
                "first_name": user_instance.first_name,
                "last_name": user_instance.last_name,
                "role": user_instance.role,
                "is_active": user_instance.is_active,
                "date_joined": user_instance.date_joined,
                "last_login": user_instance.last_login,
            }
            return Response(user_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BulkUserDeletionView(APIView):

    throttle_classes = [IPRateThrottle, UserRateThrottle]
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdminOrStaff]

    def post(self, request):
        try:
            user_ids = request.data.get("user_ids", [])
            if not user_ids:
                return Response(
                    {"error": "user_ids list is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            deleted_count = UserManagementService.bulk_user_deletion(user_ids)
            return Response({"deleted_count": deleted_count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetUserDetailsView(APIView):

    throttle_classes = [IPRateThrottle, UserRateThrottle]
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdminOrStaff]

    def get(self, request, user_id):
        try:
            result = UserManagementService.get_user_details(user_id)
            user = result["user"]
            urls = result["urls"]

            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
                "is_active": user.is_active,
                "date_joined": user.date_joined,
                "last_login": user.last_login,
            }

            urls_serializer = ResponseUrlSerializer(urls, many=True)

            response_data = {"user": user_data, "urls": urls_serializer.data}
            return Response(response_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SearchUsersView(GenericAPIView):

    throttle_classes = [IPRateThrottle, UserRateThrottle]
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdminOrStaff]

    def get(self, request):
        try:
            query = request.GET.get("q", "")
            if not query:
                return Response(
                    {"error": "Query parameter 'q' is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            limit = int(request.GET.get("limit", 10))
            page = int(request.GET.get("page", 1))

            result = UserManagementService.search_users_with_pagination(
                query, limit, page
            )

            return Response(result)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
