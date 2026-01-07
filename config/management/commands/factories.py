from api.url.models import Url, UrlStatus
from api.analytics.models import Visit
from api.admin_panel.system.models import SystemConfiguration
from api.admin_panel.audit.models import AuditLog
from api.admin_panel.fraud.models import FraudIncident
from api.url.redirection.models import RedirectionRule
import factory
import random
from hashlib import sha256
from django.utils import timezone
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from faker import Faker

User = get_user_model()

fake = Faker()


class CustomUserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username",)

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = factory.Sequence(lambda n: f'user_{n}_{fake.lexify(text="????")}')
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")

    is_active = True
    is_staff = factory.LazyAttribute(
        lambda o: o.role in [User.Role.ADMIN, User.Role.STAFF]
    )
    is_superuser = factory.LazyAttribute(lambda o: o.role == User.Role.ADMIN)
    role = factory.Faker(
        "random_element", elements=[choice[0] for choice in User.Role.choices]
    )

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        password = (
            extracted
            if extracted
            else factory.Faker(
                "password",
                length=12,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            ).generate()
        )
        self.set_password(password)

    @factory.post_generation
    def force_role(self, create, extracted, **kwargs):
        """Allows you to override the random role easily"""
        if extracted:
            self.role = extracted


class UrlStatusFactory(DjangoModelFactory):
    class Meta:
        model = UrlStatus

    state = factory.Faker(
        "random_element", elements=[choice[0] for choice in UrlStatus.State.choices]
    )
    reason = factory.Maybe(
        factory.LazyAttribute(lambda o: o.state == UrlStatus.State.ACTIVE),
        yes_declaration=None,
        no_declaration=factory.Faker("sentence", nb_words=4),
    )

    last_checked = factory.LazyFunction(
        lambda: fake.date_time_this_month(tzinfo=timezone.get_current_timezone())
    )


class UrlFactory(DjangoModelFactory):
    class Meta:
        model = Url

    name = factory.Sequence(lambda n: f"Project {fake.word() if n==0 else n}")
    long_url = factory.Faker("url")
    short_url = factory.Sequence(lambda n: f"short-{n}-{fake.lexify( text='????????')}")
    visits = factory.Faker("random_int", min=0, max=10000)
    unique_visits = factory.LazyAttribute(lambda o: random.randint(0, o.visits))
    last_accessed = factory.LazyFunction(
        lambda: fake.date_time_this_month(tzinfo=timezone.get_current_timezone())
    )
    expiry_date = factory.Faker(
        "date_time_between",
        start_date="+30d",
        end_date="+1y",
        tzinfo=timezone.get_current_timezone(),
    )
    status = factory.RelatedFactory(UrlStatusFactory, factory_related_name="url")
    is_custom_alias = factory.Faker("boolean", chance_of_getting_true=20)
    user = factory.SubFactory(CustomUserFactory)


class RedirectionRuleFactory(DjangoModelFactory):
    class Meta:
        model = RedirectionRule

    name = factory.Faker("catch_phrase")
    target_url = factory.Faker("url")
    priority = factory.Faker("random_int", min=1, max=100)
    is_active = factory.Faker("boolean", chance_of_getting_true=80)

    @factory.lazy_attribute
    def conditions(self):
        """
        Generates a realistic set of conditions for testing.
        Example: {"device_type": "mobile", "country": "US"}
        """
        possible_conditions = {
            "country": lambda: random.choice(["US", "GB", "DE", "FR", "IN"]),
            "device_type": lambda: random.choice(["mobile", "tablet", "desktop"]),
            "browser": lambda: random.choice(["Chrome", "Firefox", "Safari"]),
            "os": lambda: random.choice(["iOS", "Android", "Windows", "MacOS"]),
            "language": lambda: random.choice(["en", "es", "fr"]),
            "mobile": lambda: random.choice([True, False]),
            "referer": lambda: (
                "facebook.com" if random.random() > 0.5 else "google.com"
            ),
        }

        keys_to_use = random.sample(
            list(possible_conditions.keys()), k=random.randint(1, 3)
        )
        return {key: possible_conditions[key]() for key in keys_to_use}


class VisitFactory(DjangoModelFactory):
    class Meta:
        model = Visit

    hashed_ip = factory.LazyFunction(lambda: sha256(fake.ipv4().encode()).hexdigest())
    referer = factory.Faker("uri")
    geolocation = factory.Faker("country")
    browser = factory.Faker(
        "random_element", elements=["Chrome", "Firefox", "Safari", "Edge"]
    )
    operating_system = factory.Faker(
        "random_element", elements=["Windows", "MacOS", "Linux", "iOS", "Android"]
    )
    device = factory.Faker("random_element", elements=["Mobile", "Desktop", "Tablet"])
    new_visitor = factory.Faker("boolean", chance_of_getting_true=70)


class FraudIncidentFactory(DjangoModelFactory):
    class Meta:
        model = FraudIncident

    incident_type = factory.Faker(
        "random_element", elements=[c[0] for c in FraudIncident.INCIDENT_TYPES]
    )
    severity = factory.Faker(
        "random_element", elements=[c[0] for c in FraudIncident.SEVERITY_LEVELS]
    )

    @factory.lazy_attribute
    def details(self):
        """Generates realistic fraud metadata based on the type"""
        fake_ip = fake.ipv4()

        if self.incident_type == "burst":
            return {
                "ip": fake_ip,
                "request_count": random.randint(500, 2000),
                "time_window_seconds": 10,
                "action": "blocked",
            }
        elif self.incident_type == "suspicious_ua":
            return {
                "ip": fake_ip,
                "user_agent": "python-requests/2.25.1",
                "reason": "Known bot fingerprint",
            }
        return {"ip": fake_ip, "reason": "General violation"}


class AuditLogFactory(DjangoModelFactory):
    class Meta:
        model = AuditLog

    action = factory.Faker(
        "random_element", elements=[c[0] for c in AuditLog.Actions.choices]
    )
    ip_address = factory.Faker("ipv4")
    successful = factory.Faker("boolean", chance_of_getting_true=95)

    @factory.lazy_attribute
    def changes(self):
        """Simulates a JSON diff of what was changed."""
        if self.action == AuditLog.Actions.UPDATE:
            return {
                "name": {"old": "Old Name", "new": "New Name"},
                "is_active": {"old": True, "new": False},
            }
        elif self.action == AuditLog.Actions.CREATE:
            return {"status": "created", "initial_state": "active"}
        return {}

    @factory.lazy_attribute
    def content_type(self):
        return random.choice(["Url", "RedirectionRule", "CustomUser"])
