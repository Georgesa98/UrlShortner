from rest_framework.views import APIView, Response, status
from api.admin_panel.audit.AuditService import AuditService
from datetime import datetime
from api.custom_auth.authentication import CookieJWTAuthentication
from api.throttling import IPRateThrottle, UserRateThrottle
from rest_framework.permissions import IsAdminUser


class GetAuditLogsView(APIView):
    throttle_classes = [IPRateThrottle, UserRateThrottle]
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request):
        user_id = request.GET.get("user_id")
        action = request.GET.get("action")
        date_from_str = request.GET.get("date_from")
        date_to_str = request.GET.get("date_to")
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 10))
        sort_by = request.GET.get("sort_by", "-timestamp")

        date_from = None
        date_to = None
        if date_from_str:
            try:
                date_from = datetime.strptime(date_from_str, "%Y-%m-%d")
            except ValueError:
                return Response(
                    {"error": "Invalid date format for date_from. Use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        if date_to_str:
            try:
                date_to = datetime.strptime(date_to_str, "%Y-%m-%d")
            except ValueError:
                return Response(
                    {"error": "Invalid date format for date_to. Use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            audit_logs = AuditService.fetch_audit_logs(
                user_id=user_id,
                action=action,
                date_from=date_from,
                date_to=date_to,
                page=page,
                page_size=page_size,
                sort_by=sort_by,
            )
            return Response(audit_logs, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
