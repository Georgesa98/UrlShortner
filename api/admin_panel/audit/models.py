from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()


class AuditLog(models.Model):
    class Actions(models.TextChoices):
        CREATE = "CREATE", "create"
        UPDATE = "UPDATE", "update"
        DELETE = "DELETE", "delete"
        GET = "GET", "get"

    action = models.CharField(max_length=32, choices=Actions.choices, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    content_type = models.CharField(max_length=128, null=True, blank=True)
    content_id = models.CharField(max_length=128, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, db_index=True)
    changes = models.JSONField(default=dict, null=True, blank=True)
    successful = models.BooleanField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["timestamp", "user"]),
        ]
