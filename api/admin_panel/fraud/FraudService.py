from django.utils import timezone
from datetime import timedelta

from api.analytics.utils import get_ip_address
from .models import FraudIncident
from api.url.models import UrlStatus
from django.db.models import Count


class FraudService:
    """Service for detecting, logging, and aggregating fraud-related activities."""

    @staticmethod
    def log_incident(
        incident_type: str, details: dict, severity: str = "low", user=None, url=None
    ) -> object:
        FraudIncident.objects.create(
            incident_type=incident_type,
            details=details,
            severity=severity,
            user=user,
            url=url,
        )

    @staticmethod
    def flag_suspicious_ua(user_agent: str, request, url_instance) -> bool:
        """Flag visits with suspicious user agents.

        Args:
            user_agent (str): The user agent string.
            request: The HTTP request object.
            url_instance: The URL instance being visited.

        Returns:
            bool: True if flagged as suspicious.
        """
        if not user_agent or user_agent.strip() == "":
            # Empty UA is suspicious
            FraudService.log_incident(
                "suspicious_ua",
                {
                    "user_agent": user_agent,
                    "ip": get_ip_address(request),
                    "url": url_instance.short_url,
                },
                severity="low",
                url=url_instance,
            )
            return True

        suspicious_patterns = ["curl", "wget", "python-urllib", "go-http-client"]
        if any(pattern in user_agent.lower() for pattern in suspicious_patterns):
            FraudService.log_incident(
                "suspicious_ua",
                {
                    "user_agent": user_agent,
                    "ip": request.META.get("REMOTE_ADDR"),
                    "url": url_instance.short_url,
                    "pattern": "scripting",
                },
                severity="medium",
                url=url_instance,
            )
            return True

        return False

    @staticmethod
    def flag_burst_protection(url_instance, ip) -> None:
        """Log burst protection incidents.

        Args:
            url_instance: The URL instance.
            ip (str): The IP address triggering burst.
        """
        FraudService.log_incident(
            "burst",
            {
                "ip": ip,
                "url": url_instance.short_url,
                "reason": "Excessive requests detected",
            },
            severity="high",
            url=url_instance,
        )

    @staticmethod
    def flag_throttle_violation(request, view, rate) -> None:
        """Log throttle violations.

        Args:
            request: The HTTP request.
            view: The view instance.
            rate (str): The rate limit exceeded.
        """
        user = getattr(request, "user", None) if request.user.is_authenticated else None
        FraudService.log_incident(
            "throttle",
            {
                "ip": request.META.get("REMOTE_ADDR"),
                "user_id": user.id if user else None,
                "rate": rate,
                "endpoint": request.path,
            },
            severity="medium",
            user=user,
        )

    @staticmethod
    def get_overview_metrics(days: int = 7) -> dict:
        """Get aggregated fraud metrics for the last N days."""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        incidents = (
            FraudIncident.objects.filter(created_at__gte=start_date)
            .values("incident_type")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        flagged_urls = UrlStatus.objects.filter(
            state=UrlStatus.State.FLAGGED, url__created_at__gte=start_date
        ).count()

        total_incidents = sum(inc["count"] for inc in incidents)
        risk_score = "low"
        if total_incidents > 10 or flagged_urls > 5:
            risk_score = "medium"
        if total_incidents > 50 or flagged_urls > 20:
            risk_score = "high"

        return {
            "period_days": days,
            "total_incidents": total_incidents,
            "incidents_by_type": list(incidents),
            "flagged_urls": flagged_urls,
            "risk_score": risk_score,
            "top_incident_types": [inc["incident_type"] for inc in incidents[:3]],
        }

    @staticmethod
    def flag_suspicious_ua(user_agent: str, request, url_instance) -> bool:
        """Flag visits with suspicious user agents.

        Args:
            user_agent (str): The user agent string.
            request: The HTTP request object.
            url_instance: The URL instance being visited.

        Returns:
            bool: True if flagged as suspicious.
        """
        if not user_agent or user_agent.strip() == "":
            # Empty UA is suspicious
            FraudService.log_incident(
                "suspicious_ua",
                {
                    "user_agent": user_agent,
                    "ip": request.META.get("REMOTE_ADDR"),
                    "url": url_instance.short_url,
                },
                severity="low",
                url=url_instance,
            )
            return True

        suspicious_patterns = ["curl", "wget", "python-urllib", "go-http-client"]
        if any(pattern in user_agent.lower() for pattern in suspicious_patterns):
            FraudService.log_incident(
                "suspicious_ua",
                {
                    "user_agent": user_agent,
                    "ip": request.META.get("REMOTE_ADDR"),
                    "url": url_instance.short_url,
                    "pattern": "scripting",
                },
                severity="medium",
                url=url_instance,
            )
            return True

        return False

    @staticmethod
    def flag_burst_protection(url_instance, ip) -> None:
        """Log burst protection incidents.

        Args:
            url_instance: The URL instance.
            ip (str): The IP address triggering burst.
        """
        FraudService.log_incident(
            "burst",
            {
                "ip": ip,
                "url": url_instance.short_url,
                "reason": "Excessive requests detected",
            },
            severity="high",
            url=url_instance,
        )

    @staticmethod
    def flag_throttle_violation(request, view, rate) -> None:
        """Log throttle violations.

        Args:
            request: The HTTP request.
            view: The view instance.
            rate (str): The rate limit exceeded.
        """
        user = getattr(request, "user", None) if request.user.is_authenticated else None
        FraudService.log_incident(
            "throttle",
            {
                "ip": request.META.get("REMOTE_ADDR"),
                "user_id": user.id if user else None,
                "rate": rate,
                "endpoint": request.path,
            },
            severity="medium",
            user=user,
        )
