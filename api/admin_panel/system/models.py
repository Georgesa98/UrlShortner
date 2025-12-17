from django.db import models


class SystemConfiguration(models.Model):
    key = models.CharField(max_length=128, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
