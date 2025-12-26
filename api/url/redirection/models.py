from django.db import models
from api.url.models import Url

# Create your models here.


class RedirectionRule(models.Model):
    CONDITION_KEYS = [
        "country",
        "device_type",
        "browser",
        "os",
        "language",
        "time_range",
        "mobile",
        "referer",
    ]

    name = models.CharField(max_length=255, help_text="Descriptive name for the rule")
    url = models.ForeignKey(
        Url,
        on_delete=models.CASCADE,
        related_name="redirection_rules",
        help_text="Associated short URL",
    )
    conditions = models.JSONField(
        default=dict, help_text="JSON conditions for when this rule applies"
    )
    target_url = models.URLField(
        max_length=2000, help_text="Redirect destination URL when conditions match"
    )
    priority = models.IntegerField(
        default=0, help_text="Rule priority (higher = checked first)"
    )
    is_active = models.BooleanField(default=True, help_text="Whether rule is enabled")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-priority", "created_at"]
        indexes = [
            models.Index(fields=["url", "priority"]),
            models.Index(fields=["is_active"]),
        ]
