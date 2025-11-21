from django.core.management.base import BaseCommand
from datetime import datetime, timezone
from api.url.models import Url, UrlStatus


class Command(BaseCommand):
    def handle(self, *args, **options):
        expired_urls = Url.objects.filter(
            expiration_date__lte=datetime.now(timezone.utc)
        ).select_related("url_status")
        count = UrlStatus.objects.filter(
            url__in=expired_urls, state=UrlStatus.State.ACTIVE
        ).update(
            state=UrlStatus.State.EXPIRED,
            reason="URL expired on {}".format(datetime.now(timezone.utc).isoformat()),
        )
        self.stdout.write(self.style.SUCCESS(f"Deactivated {count} expired URLs."))
