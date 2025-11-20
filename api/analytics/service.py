from api.analytics.models import Visit
from api.analytics.utils import get_ip_address, hash_ip, ip_address_match
from datetime import datetime, timezone


class AnalyticsService:
    @classmethod
    def record_visit(self, request, url_instance):
        ip = get_ip_address(request)
        url_instance.visits += 1
        if not ip_address_match(ip):
            hashed_ip = hash_ip(ip)
            url_instance.unique_visits += 1
            url_instance.last_accessed = datetime.now(timezone.utc)
            url_instance.save()
            Visit.objects.create(
                url=url_instance,
                hashed_ip=hashed_ip,
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                referrer=request.META.get("HTTP_REFERRER", ""),
            )

    @classmethod
    def get_top_visited_urls(self, user_id: int, num: int):
        from api.url.models import Url

        return Url.objects.filter(user_id=user_id).order_by("-visits")[:num]
