from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from api.url.models import Url, UrlStatus
from api.analytics.models import Visit
from api.admin_panel.audit.models import AuditLog
from api.admin_panel.fraud.models import FraudIncident
from api.admin_panel.system.models import SystemConfiguration
from api.url.redirection.models import RedirectionRule
from pathlib import Path
import json
from typing import Dict, Any

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds the database with initial data for development"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before seeding",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Starting database seeding..."))

        if options["clear"]:
            self.clear_data()

        seed_file_path = self._get_seed_file_path()

        if not seed_file_path.exists():
            self.stdout.write(
                self.style.ERROR(f"Seed data file not found: {seed_file_path}")
            )
            return

        try:
            with open(seed_file_path, "r") as f:
                seed_data = json.load(f)
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f"Error parsing JSON file: {e}"))
            return

        # Process all data in a transaction for data integrity
        with transaction.atomic():
            self._process_seed_data(seed_data)

        self.stdout.write(
            self.style.SUCCESS("✓ Database seeding completed successfully!")
        )

    def _get_seed_file_path(self) -> Path:
        """Get the path to the seed data JSON file"""
        return Path(__file__).resolve().parent / "seed_data.json"

    def clear_data(self):
        """Clear existing data from all tables"""
        self.stdout.write(self.style.WARNING("Clearing existing data..."))

        models_to_clear = [
            (Visit, "Visits"),
            (AuditLog, "Audit Logs"),
            (FraudIncident, "Fraud Incidents"),
            (RedirectionRule, "Redirection Rules"),
            (UrlStatus, "URL Statuses"),
            (Url, "URLs"),
            (SystemConfiguration, "System Configurations"),
            (User, "Users"),
        ]

        for model, name in models_to_clear:
            count = model.objects.all().delete()[0]
            self.stdout.write(f"  Deleted {count} {name}")

    def _process_seed_data(self, seed_data: list):
        """Process seed data and create database objects"""
        created_objects = {}

        # Define the order of processing to handle foreign key dependencies
        model_handlers = {
            "custom_auth.customuser": self._create_user,
            "url.url": self._create_url,
            "url.urlstatus": self._create_url_status,
            "analytics.visit": self._create_visit,
            "admin_panel.auditlog": self._create_audit_log,
            "fraud.fraudincident": self._create_fraud_incident,
            "system.systemconfiguration": self._create_system_configuration,
            "redirection.redirectionrule": self._create_redirection_rule,
        }

        for item in seed_data:
            model_name = item["model"]
            pk = item["pk"]
            fields = item["fields"]

            handler = model_handlers.get(model_name)
            if handler:
                handler(fields, created_objects, pk)
            else:
                self.stdout.write(self.style.WARNING(f"Unknown model: {model_name}"))

    def _parse_datetime(self, datetime_str: str):
        """Parse datetime string handling various formats"""
        if not datetime_str:
            return None

        # Replace 'Z' with '+00:00' for timezone
        datetime_str = datetime_str.replace("Z", "+00:00")

        # Handle incomplete seconds format (e.g., '2024-05-14T12:00:0+00:00')
        if datetime_str.count(":") == 2 and datetime_str.endswith("+00:00"):
            parts = datetime_str.split(":")
            if len(parts) == 3:
                seconds_part = parts[2].replace("+00:00", "")
                if len(seconds_part) == 1:
                    # Fix single digit seconds
                    datetime_str = f"{parts[0]}:{parts[1]}:0{seconds_part}+00:00"

        return timezone.datetime.fromisoformat(datetime_str)

    def _create_user(self, fields: Dict[str, Any], created_objects: Dict, pk: int):
        """Create a user with the given fields"""
        user_data = {
            "username": fields["username"],
            "email": fields["email"],
            "first_name": fields.get("first_name", ""),
            "last_name": fields.get("last_name", ""),
            "role": fields.get("role", "USER"),
            "is_active": fields.get("is_active", True),
            "is_staff": fields.get("is_staff", False),
            "is_superuser": fields.get("is_superuser", False),
            "date_joined": self._parse_datetime(fields.get("date_joined"))
            or timezone.now(),
        }

        user, created = User.objects.get_or_create(
            username=user_data["username"], defaults=user_data
        )

        # Set password using Django's secure password hashing
        if "password" in fields:
            user.set_password(fields["password"])
            user.save()

        created_objects[f"custom_auth.customuser_{pk}"] = user
        status = "Created" if created else "Updated"
        self.stdout.write(f"  {status} user: {user.username} ({user.role})")

    def _create_url(self, fields: Dict[str, Any], created_objects: Dict, pk: int):
        """Create a URL with the given fields"""
        user = self._get_related_object(
            created_objects, "custom_auth.customuser", fields.get("user")
        )

        url_data = {
            "name": fields.get("name"),
            "long_url": fields["long_url"],
            "short_url": fields["short_url"],
            "created_at": self._parse_datetime(fields.get("created_at"))
            or timezone.now(),
            "updated_at": self._parse_datetime(fields.get("updated_at"))
            or timezone.now(),
            "visits": fields.get("visits", 0),
            "unique_visits": fields.get("unique_visits", 0),
            "last_accessed": self._parse_datetime(fields.get("last_accessed")),
            "expiry_date": self._parse_datetime(fields.get("expiry_date")),
            "is_custom_alias": fields.get("is_custom_alias", False),
            "user": user,
        }

        url, created = Url.objects.get_or_create(
            short_url=url_data["short_url"], defaults=url_data
        )

        created_objects[f"url.url_{pk}"] = url
        status = "Created" if created else "Updated"
        self.stdout.write(f"  {status} URL: {url.short_url} -> {url.name}")

    def _create_url_status(
        self, fields: Dict[str, Any], created_objects: Dict, pk: int
    ):
        """Create a URL status with the given fields"""
        url = self._get_related_object(created_objects, "url.url", fields.get("url"))

        if not url:
            self.stdout.write(
                self.style.WARNING(f"  Skipping URL status {pk}: URL not found")
            )
            return

        url_status_data = {
            "url": url,
            "state": fields["state"],
            "reason": fields.get("reason"),
            "last_checked": self._parse_datetime(fields.get("last_checked"))
            or timezone.now(),
        }

        url_status, created = UrlStatus.objects.update_or_create(
            url=url, defaults=url_status_data
        )

        created_objects[f"url.urlstatus_{pk}"] = url_status
        status = "Created" if created else "Updated"
        self.stdout.write(
            f"  {status} URL status: {url.short_url} ({url_status.state})"
        )

    def _create_visit(self, fields: Dict[str, Any], created_objects: Dict, pk: int):
        """Create a visit with the given fields"""
        url = self._get_related_object(created_objects, "url.url", fields.get("url"))

        if not url:
            self.stdout.write(
                self.style.WARNING(f"  Skipping visit {pk}: URL not found")
            )
            return

        visit_data = {
            "url": url,
            "timestamp": self._parse_datetime(fields.get("timestamp"))
            or timezone.now(),
            "hashed_ip": fields["hashed_ip"],
            "referer": fields.get("referer"),
            "geolocation": fields.get("geolocation"),
            "browser": fields.get("browser"),
            "operating_system": fields.get("operating_system"),
            "device": fields.get("device"),
            "new_visitor": fields.get("new_visitor", True),
        }

        visit = Visit.objects.create(**visit_data)
        created_objects[f"analytics.visit_{pk}"] = visit
        self.stdout.write(f"  Created visit for URL: {visit.url.short_url}")

    def _create_audit_log(self, fields: Dict[str, Any], created_objects: Dict, pk: int):
        """Create an audit log with the given fields"""
        user = self._get_related_object(
            created_objects, "custom_auth.customuser", fields.get("user")
        )

        audit_log_data = {
            "action": fields["action"],
            "timestamp": self._parse_datetime(fields.get("timestamp"))
            or timezone.now(),
            "user": user,
            "content_type": fields.get("content_type"),
            "content_id": fields.get("content_id"),
            "ip_address": fields.get("ip_address"),
            "changes": fields.get("changes", {}),
            "successful": fields.get("successful", True),
        }

        audit_log = AuditLog.objects.create(**audit_log_data)
        created_objects[f"admin_panel.auditlog_{pk}"] = audit_log

        user_info = audit_log.user.username if audit_log.user else "System"
        self.stdout.write(f"  Created audit log: {audit_log.action} by {user_info}")

    def _create_fraud_incident(
        self, fields: Dict[str, Any], created_objects: Dict, pk: int
    ):
        """Create a fraud incident with the given fields"""
        user = self._get_related_object(
            created_objects, "custom_auth.customuser", fields.get("user")
        )
        url = self._get_related_object(created_objects, "url.url", fields.get("url"))

        fraud_incident_data = {
            "incident_type": fields["incident_type"],
            "details": fields["details"],
            "severity": fields["severity"],
            "user": user,
            "url": url,
            "created_at": self._parse_datetime(fields.get("created_at"))
            or timezone.now(),
        }

        fraud_incident = FraudIncident.objects.create(**fraud_incident_data)
        created_objects[f"fraud.fraudincident_{pk}"] = fraud_incident
        self.stdout.write(
            f"  Created fraud incident: {fraud_incident.incident_type} "
            f"(severity: {fraud_incident.severity})"
        )

    def _create_system_configuration(
        self, fields: Dict[str, Any], created_objects: Dict, pk: int
    ):
        """Create a system configuration with the given fields"""
        system_config_data = {
            "key": fields["key"],
            "value": fields["value"],
            "description": fields.get("description", ""),
            "updated_at": self._parse_datetime(fields.get("updated_at"))
            or timezone.now(),
        }

        system_config, created = SystemConfiguration.objects.update_or_create(
            key=system_config_data["key"], defaults=system_config_data
        )

        created_objects[f"system.systemconfiguration_{pk}"] = system_config
        status = "Created" if created else "Updated"
        self.stdout.write(
            f"  {status} system config: {system_config.key} = {system_config.value}"
        )

    def _create_redirection_rule(
        self, fields: Dict[str, Any], created_objects: Dict, pk: int
    ):
        """Create a redirection rule with the given fields"""
        url = self._get_related_object(created_objects, "url.url", fields.get("url"))

        if not url:
            self.stdout.write(
                self.style.WARNING(f"  Skipping redirection rule {pk}: URL not found")
            )
            return

        redirection_rule_data = {
            "name": fields["name"],
            "url": url,
            "conditions": fields["conditions"],
            "target_url": fields["target_url"],
            "priority": fields.get("priority", 0),
            "is_active": fields.get("is_active", True),
            "created_at": self._parse_datetime(fields.get("created_at"))
            or timezone.now(),
            "updated_at": self._parse_datetime(fields.get("updated_at"))
            or timezone.now(),
        }

        redirection_rule = RedirectionRule.objects.create(**redirection_rule_data)
        created_objects[f"redirection.redirectionrule_{pk}"] = redirection_rule

        status = "Active" if redirection_rule.is_active else "Inactive"
        self.stdout.write(
            f"  Created redirection rule: {redirection_rule.name} ({status})"
        )

    def _get_related_object(self, created_objects: Dict, model_prefix: str, pk: int):
        """Get a related object from the created objects cache"""
        if pk is None:
            return None

        key = f"{model_prefix}_{pk}"
        return created_objects.get(key)
