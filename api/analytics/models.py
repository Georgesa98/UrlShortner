from django.db import models

from api.url.models import Url

# Create your models here.


class Visit(models.Model):
    url = models.ForeignKey(Url, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    hashed_ip = models.CharField(max_length=64)
    referrer = models.TextField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
