from django.db import models
from buckets.fields import S3FileField

TYPES = ['image/jpeg', 'application/gpx+xml', 'text/plain']


class FileModel(models.Model):
    name = models.CharField(max_length=200)
    file = S3FileField(upload_to='test', accepted_types=TYPES,
                       null=True, blank=True)
