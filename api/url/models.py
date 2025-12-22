from django.db import models
from django.conf import settings
from datetime import datetime, timezone


# Create your models here.
class Url(models.Model):
    name = models.CharField(max_length=512, unique=True, null=True, blank=True)
    long_url = models.CharField(max_length=2000)
    short_url = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    visits = models.IntegerField(default=0)
    unique_visits = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True, db_index=True)
    expiry_date = models.DateTimeField(null=True, blank=True, db_index=True)
    is_custom_alias = models.BooleanField(default=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_index=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=["user", "created_at"]),
        ]

    @property
    def days_until_expiry(self) -> int | None:
        if self.expiry_date:
            if isinstance(self.expiry_date, str):
                expiry = datetime.fromisoformat(self.expiry_date)
            else:
                expiry = self.expiry_date

            days = (expiry - datetime.now(timezone.utc)).days
            return days if days >= 0 else None
        return None


class UrlStatus(models.Model):
    class State(models.TextChoices):
        ACTIVE = "ACTIVE", "active"
        EXPIRED = "EXPIRED", "expired"
        FLAGGED = "FLAGGED", "flagged"
        DISABLED = "DISABLED", "disabled"
        SUSPENDED = "SUSPENDED", "suspended"

    url = models.OneToOneField(Url, on_delete=models.CASCADE, related_name="url_status")
    state = models.CharField(
        max_length=16, choices=State.choices, default=State.ACTIVE, db_index=True
    )
    reason = models.CharField(max_length=256, null=True, blank=True)
