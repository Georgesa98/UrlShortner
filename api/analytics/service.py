from api.analytics.models import Visit
from api.analytics.utils import (
    convert_ip_to_location,
    get_ip_address,
    hash_ip,
    ip_address_match,
    parse_user_agent,
)
from datetime import datetime, timezone, timedelta
from django.db.models import Count, Q
from api.url.models import Url, UrlStatus


class AnalyticsService:

    @staticmethod
    def record_visit(request, url_instance):
        ip = get_ip_address(request)
        country = convert_ip_to_location(ip)
        user_agent = parse_user_agent(request.META.get("HTTP_USER_AGENT", ""))
        url_instance.visits += 1
        hashed_ip = hash_ip(ip)
        is_new_visitor = ip_address_match(hashed_ip)
        if not is_new_visitor:
            url_instance.unique_visits += 1
            url_instance.last_accessed = datetime.now(timezone.utc)
        url_instance.save()
        Visit.objects.create(
            url=url_instance,
            hashed_ip=hashed_ip,
            geolocation=country,
            operating_system=user_agent["os"],
            browser=user_agent["browser"],
            device=user_agent["device"],
            referrer=request.META.get("HTTP_REFERRER", ""),
            new_visiter=is_new_visitor,
        )

    @staticmethod
    def get_top_visited_urls(user_id: int, num: int):
        from api.url.models import Url

        return Url.objects.filter(user_id=user_id).order_by("-visits")[:num]

    @staticmethod
    def get_url_summary(url_id: str, range_days: int = 7):
        url_instance = Url.objects.select_related("url_status").get(id=url_id)

        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=range_days)

        visit_queryset = Visit.objects.filter(url=url_id, timestamp__gte=start_date)

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
