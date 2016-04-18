from django.utils.translation import ugettext as _
from django.core.files.storage import default_storage
from django.db import models


class S3File(object):
    def __init__(self, url=None):
        assert url, _("Cannot initialize S3File, url not set")

        self.url = url
    # have a look at https://github.com/django/django/blob/master/django/db/models/fields/files.py
    # this is pretty much what we need here


class S3FileField(models.URLField):
    attr_class = S3File

    def __init__(self, upload_to='', storage=None, *args, **kwargs):
        self.storage = storage or default_storage
        self.upload_to = upload_to

        kwargs['max_length'] = kwargs.get('max_length', 200)
        super(S3FileField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(S3FileField, self).deconstruct()

        if self.upload_to != '':
            kwargs['upload_to'] = self.upload_to

        if self.storage != default_storage:
            kwargs['storage'] = self.storage

        if kwargs.get('max_length') == 200:
            del kwargs['max_length']

        return name, path, args, kwargs

    def from_db_value(self, value, expression, connection, context):
        return S3File(url=value)

    def to_python(self, value):
        if value is None or isinstance(value, S3File):
            return value

        return S3File(url=value)
