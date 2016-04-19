from django.db import models
from buckets.fields import S3FileField


class FileModel(models.Model):
    name = models.CharField(max_length=200)
    file = S3FileField()
