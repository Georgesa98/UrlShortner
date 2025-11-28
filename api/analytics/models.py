from django.db import models

from api.url.models import Url

# Create your models here.


class Visit(models.Model):
    url = models.ForeignKey(Url, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    hashed_ip = models.CharField(max_length=64)
    referrer = models.TextField(blank=True, null=True)
    geolocation = models.CharField(max_length=128, blank=True, null=True)
    browser = models.CharField(max_length=64, blank=True, null=True)
    operating_system = models.CharField(max_length=64, blank=True, null=True)
    device = models.CharField(max_length=64, blank=True, null=True)
    new_visitor = models.BooleanField(default=True)
