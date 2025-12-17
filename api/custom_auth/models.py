from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "admin"
        STAFF = "STAFF", "staff"
        USER = "USER", "user"

    role = models.CharField(
        choices=Role.choices, max_length=32, default=Role.USER, db_index=True
    )
