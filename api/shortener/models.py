from django.db import models


# Create your models here.
class Url(models.Model):
    long_url = models.CharField(max_length=4096)
    short_url = models.CharField(max_length=100, unique=True)
