from django.db import models

from api.url.models import Url

# Create your models here.


class Visit(models.Model):
    url = models.ForeignKey(Url, on_delete=models.CASCADE, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    hashed_ip = models.CharField(max_length=64)
    referer = models.TextField(blank=True, null=True)
    geolocation = models.CharField(max_length=128, blank=True, null=True, db_index=True)
    browser = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    operating_system = models.CharField(
        max_length=64, blank=True, null=True, db_index=True
    )
    device = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    new_visitor = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["url", "timestamp"]),
        ]
