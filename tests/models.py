from django.db import models
from buckets.fields import S3FileField


class FileModel(models.Model):
    s3_file = S3FileField()
