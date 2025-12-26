from django.core.management.base import BaseCommand
from datetime import datetime, timezone
from api.url.models import Url, UrlStatus


class Command(BaseCommand):
    def handle(self, *args, **options):
        expired_urls = Url.objects.filter(
            expiry_date__lte=timezone.now()
        ).select_related("url_status")
        from django.utils import timezone

        count = UrlStatus.objects.filter(
            url__in=expired_urls, state=UrlStatus.State.ACTIVE
        ).update(
            state=UrlStatus.State.EXPIRED,
            reason="URL expired on {}".format(timezone.now().isoformat()),
            last_checked=timezone.now(),
        )
        self.stdout.write(self.style.SUCCESS(f"Deactivated {count} expired URLs."))
