import json
from api.analytics.models import Visit
from config.redis_utils import get_redis_client
from api.analytics.utils import (
    convert_ip_to_location,
    get_ip_address,
    hash_ip,
    ip_address_match,
    parse_user_agent,
)
from config.settings_utils import get_analytics_track_ip
from datetime import datetime, timezone, timedelta
from django.db.models import Count, Q
from api.url.models import Url
from api.admin_panel.fraud.FraudService import FraudService


class AnalyticsService:
    """Service for recording and analyzing URL visit data."""

    @staticmethod
    def record_visit(request, url_instance):
        """Record a visit to a URL with analytics data.

        Args:
            request: The HTTP request object.
            url_instance (Url): The URL instance being visited.
        """
        track_ip = get_analytics_track_ip()
        if track_ip:
            ip = get_ip_address(request)
            country = convert_ip_to_location(ip)
            hashed_ip = hash_ip(ip)
            is_new_visitor = ip_address_match(hashed_ip)
        else:
            ip = None
            country = None
            hashed_ip = None
            is_new_visitor = False

        raw_ua = request.META.get("HTTP_USER_AGENT", "")
        user_agent = parse_user_agent(raw_ua)
        FraudService.flag_suspicious_ua(raw_ua, request, url_instance)
        url_instance.visits += 1
        if track_ip and not is_new_visitor:
            url_instance.unique_visits += 1
        url_instance.last_accessed = datetime.now(timezone.utc)
        url_instance.save()
        try:
            redis_conn = get_redis_client()
            visit_data = {
                "url_id": url_instance.id,
                "hashed_ip": hashed_ip,
                "geolocation": country,
                "operating_system": user_agent["os"],
                "browser": user_agent["browser"],
                "device": user_agent["device"],
                "referrer": request.META.get("HTTP_REFERRER", ""),
                "new_visitor": is_new_visitor,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            redis_conn.rpush("analytics:visits", json.dumps(visit_data))
        except Exception:
            Visit.objects.create(
                url=url_instance,
                hashed_ip=hashed_ip,
                geolocation=country,
                operating_system=user_agent["os"],
                browser=user_agent["browser"],
                device=user_agent["device"],
                referrer=request.META.get("HTTP_REFERRER", ""),
                new_visitor=is_new_visitor,
            )

    @staticmethod
    def get_top_visited_urls(user_id: int, num: int):
        """Get the top visited URLs for a user.

        Args:
            user_id (int): The user ID.
            num (int): Number of top URLs to return.

        Returns:
            QuerySet: Top visited URLs ordered by visit count.
        """
        from api.url.models import Url

        return (
            Url.objects.select_related("url_status", "user")
            .filter(user_id=user_id)
            .order_by("-visits")[:num]
        )

    @staticmethod
    def get_url_summary(url_id: str, range_days: int = 7):
        """Get detailed analytics summary for a URL.

        Args:
            url_id (str): The URL ID.
            range_days (int, optional): Number of days for analytics range. Defaults to 7.

        Returns:
            dict: Analytics data including basic info, daily visits, top metrics, and recent visitors.
        """
        url_instance = Url.objects.select_related("url_status").get(id=url_id)

        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=range_days)

        visit_queryset = Visit.objects.select_related("url").filter(
            url=url_id, timestamp__gte=start_date
        )

        top_devices = (
            visit_queryset.values("device")
            .annotate(count=Count("id"))
            .order_by("-count")[:3]
        )

        top_browsers = (
            visit_queryset.values("browser")
            .annotate(count=Count("id"))
            .order_by("-count")[:3]
        )

        top_os = (
            visit_queryset.values("operating_system")
            .annotate(count=Count("id"))
            .order_by("-count")[:3]
        )

        top_countries = (
            visit_queryset.values("geolocation")
            .annotate(count=Count("id"))
            .order_by("-count")[:3]
        )

        daily_visits = (
            visit_queryset.extra({"date": "DATE(timestamp)"})
            .values("date")
            .annotate(
                daily_visits=Count("id"),
                unique_visits=Count("id", filter=Q(new_visitor=True)),
            )
        ).order_by("date")

        recent_visitors = visit_queryset.order_by("-timestamp")[:50]

        return {
            "basic_info": {
                "id": url_instance.id,
                "long_url": url_instance.long_url,
                "short_url": url_instance.short_url,
                "created_at": url_instance.created_at,
                "updated_at": url_instance.updated_at,
                "visits": url_instance.visits,
                "unique_visits": url_instance.unique_visits,
                "expiry_date": url_instance.expiry_date,
            },
            "analytics": {
                "daily_visits": list(daily_visits),
                "unique_vs_total": {
                    "unique": url_instance.unique_visits,
                    "total": url_instance.visits,
                },
            },
            "top_metrics": {
                "devices": list(top_devices),
                "browsers": list(top_browsers),
                "operating_systems": list(top_os),
                "countries": list(top_countries),
            },
            "recent_visitors": recent_visitors,
        }
