from api.admin_panel.audit.models import AuditLog
from api.analytics.utils import anonymize_ip
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from datetime import datetime

User = get_user_model()


class AuditService:
    """Service for audit logging and retrieval."""

    @staticmethod
    def initiate_log(
        action: str,
        ip_address: str,
        user_id: str = None,
    ):
        """Create initial audit log entry.

        Args:
            action (str): The action being performed.
            ip_address (str): The IP address of the request.
            user_id (str, optional): The user ID performing the action.

        Returns:
            AuditLog: The created audit log instance.
        """
        hidden_ip = anonymize_ip(ip_address)
        user_instance = None
        if user_id:
            try:
                user_instance = User.objects.get(id=user_id)
            except User.DoesNotExist:
                user_instance = None
        initialize_audit = AuditLog.objects.create(
            action=action,
            ip_address=hidden_ip,
            user=user_instance,  # Use user instead of user_id
        )
        return initialize_audit

    @staticmethod
    def audit_log(
        audit_id: str,
        content_type: str,
        content_id: str,
        successful: bool,
        changes: dict = None,
    ):
        """Update audit log with completion details.

        Args:
            audit_id (str): The audit log ID to update.
            content_type (str): Type of content affected.
            content_id (str): ID of the affected content.
            successful (bool): Whether the action was successful.
            changes (dict, optional): Details of changes made.
        """
        audit_instance = AuditLog.objects.get(id=audit_id)
        audit_instance.content_id = content_id
        audit_instance.content_type = content_type
        audit_instance.successful = successful
        audit_instance.changes = changes
        audit_instance.save()

    @staticmethod
    def fetch_audit_logs(
        user_id=None,
        action=None,
        date_from=None,
        date_to=None,
        page=1,
        page_size=10,
        sort_by="-timestamp",
    ):
        """Fetch paginated audit logs with filtering.

        Args:
            user_id (str, optional): Filter by user ID.
            action (str, optional): Filter by action.
            date_from (datetime, optional): Filter from date.
            date_to (datetime, optional): Filter to date.
            page (int, optional): Page number. Defaults to 1.
            page_size (int, optional): Items per page. Defaults to 10.
            sort_by (str, optional): Sort field. Defaults to "-timestamp".

        Returns:
            dict: Paginated audit logs with metadata.
        """
        queryset = AuditLog.objects.select_related("user").all()

        if user_id:
            queryset = queryset.filter(user_id=user_id)

        if action:
            queryset = queryset.filter(action=action)

        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)

        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)

        queryset = queryset.order_by(sort_by)

        paginator = Paginator(queryset, page_size)
        paginated_result = paginator.get_page(page)

        result_data = []
        for log in paginated_result:
            log_data = {
                "id": log.id,
                "action": log.action,
                "timestamp": log.timestamp,
                "user_id": log.user.id if log.user else None,
                "user_email": log.user.email if log.user else None,
                "content_type": log.content_type,
                "content_id": log.content_id,
                "ip_address": log.ip_address,
                "changes": log.changes,
                "successful": log.successful,
            }
            result_data.append(log_data)

        return {
            "data": result_data,
            "pagination": {
                "current_page": paginated_result.number,
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "has_next": paginated_result.has_next(),
                "has_previous": paginated_result.has_previous(),
            },
        }
