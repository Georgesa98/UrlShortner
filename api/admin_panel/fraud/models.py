from django.db import models
from django.contrib.auth import get_user_model
from api.url.models import Url

# Create your models here.

User = get_user_model()


class FraudIncident(models.Model):
    INCIDENT_TYPES = [
        ("burst", "Burst Protection Triggered"),
        ("throttle", "Throttle Violation"),
        ("suspicious_ua", "Suspicious User Agent"),
        ("other", "Other"),
    ]

    SEVERITY_LEVELS = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    incident_type = models.CharField(
        max_length=20,
        choices=INCIDENT_TYPES,
        help_text="Type of fraud incident detected.",
    )
    details = models.JSONField(
        help_text="JSON details of the incident (e.g., IP, URL, timestamp)."
    )
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_LEVELS,
        default="low",
        help_text="Severity level of the incident.",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User associated with the incident, if applicable.",
    )
    url = models.ForeignKey(
        Url,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="URL associated with the incident, if applicable.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Timestamp when the incident was logged."
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Fraud Incident"
        verbose_name_plural = "Fraud Incidents"
        indexes = [
            models.Index(fields=["incident_type"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["severity"]),
        ]
