from django.core.management.base import BaseCommand
from api.url.services.ShortCodeService import ShortCodeService


class Command(BaseCommand):
    def handle(self, *args, **options):
        generated = ShortCodeService().refill_pool()
        self.stdout.write(
            self.style.SUCCESS(f"Refilled shortcode pool with {generated} shortcodes.")
        )
