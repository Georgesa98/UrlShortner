from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
import random
import factory
from .factories import (
    AuditLogFactory,
    CustomUserFactory,
    UrlFactory,
    FraudIncidentFactory,
    VisitFactory,
    RedirectionRuleFactory,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds the database and provides login credentials."

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=5, help="Number of users")
        parser.add_argument(
            "--urls-per-user", type=int, default=20, help="URLs per user"
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🛠 Initializing Big Patch Seed..."))

        DEFAULT_PASSWORD = "Password123!"
        user_credentials = []

        admin = CustomUserFactory(
            role="ADMIN", username="admin_tester", password=DEFAULT_PASSWORD
        )
        user_credentials.append({"user": admin.username, "role": "ADMIN"})

        num_users = options["users"]
        for i in range(num_users):
            user = CustomUserFactory(password=DEFAULT_PASSWORD)
            user_credentials.append({"user": user.username, "role": user.role})

            num_urls = options["urls_per_user"]
            urls = UrlFactory.create_batch(num_urls, user=user)

            for url in urls:
                VisitFactory.create_batch(random.randint(50, 150), url=url)

                if random.random() > 0.6:
                    RedirectionRuleFactory.create_batch(random.randint(1, 4), url=url)

                if random.random() > 0.8:
                    FraudIncidentFactory.create(url=url, user=user, severity="high")

                AuditLogFactory.create(
                    action="CREATE",
                    user=user,
                    content_type="Url",
                    content_id=str(url.id),
                )

        self.stdout.write("\n" + "=" * 40)
        self.stdout.write(self.style.SUCCESS("✅ SEEDING COMPLETE"))
        self.stdout.write("=" * 40)
        self.stdout.write(f"Common Password: {DEFAULT_PASSWORD}")
        self.stdout.write("-" * 40)
        self.stdout.write(f"{'Username':<20} | {'Role':<10}")
        self.stdout.write("-" * 40)
        for cred in user_credentials:
            self.stdout.write(f"{cred['user']:<20} | {cred['role']:<10}")
        self.stdout.write("=" * 40 + "\n")
