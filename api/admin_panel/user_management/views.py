from rest_framework.views import APIView
from rest_framework import status
from rest_framework.generics import GenericAPIView
from api.custom_auth.authentication import CookieJWTAuthentication
from api.throttling import IPRateThrottle, UserRateThrottle
from api.admin_panel.user_management.UserManagementService import UserManagementService
from api.url.serializers.UrlSerializer import ResponseUrlSerializer
from api.custom_auth.permissions import IsAdminOrStaff
from config.utils.responses import SuccessResponse, ErrorResponse
from django.contrib.auth import get_user_model

User = get_user_model()


# Create your views here.
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

            return SuccessResponse(
                data=result,
                message="Users retrieved successfully",
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return ErrorResponse(
                message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
            return SuccessResponse(
                data=user_data,
                message="User ban status toggled successfully",
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


class BulkUserDeletionView(APIView):
    throttle_classes = [IPRateThrottle, UserRateThrottle]
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdminOrStaff]

    def post(self, request):
        try:
            user_ids = request.data.get("user_ids", [])
            if not user_ids:
                return ErrorResponse(
                    message="user_ids list is required",
                    status=status.HTTP_400_BAD_REQUEST,
                )

            deleted_count = UserManagementService.bulk_user_deletion(user_ids)
            return SuccessResponse(
                data={"deleted_count": deleted_count},
                message="Users deleted successfully",
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return ErrorResponse(
                message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
            return SuccessResponse(
                data=response_data,
                message="User details retrieved successfully",
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
