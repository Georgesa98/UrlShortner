from api.admin_panel.audit.models import AuditLog
from api.analytics.utils import anonymize_ip
from django.contrib.auth import get_user_model

User = get_user_model()


class AuditService:
    @staticmethod
    def initiate_log(
        action: str,
        ip_address: str,
        user_id: str = None,
    ):
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
        audit_instance = AuditLog.objects.get(id=audit_id)
        audit_instance.content_id = content_id
        audit_instance.content_type = content_type
        audit_instance.successful = successful
        audit_instance.changes = changes
        audit_instance.save()
