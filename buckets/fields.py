
import os
from django.core.files.storage import default_storage
from django.db import models


class S3File(object):
    def __init__(self, url, field):
        self.field = field
        self.storage = field.storage
        self.url = url
        self.committed = True

    def _get_file(self):
        if not hasattr(self, '_file') or not self._file:
            self._file = self.storage.open(self.url)

    def _set_file(self, file):
        self._file = file
        self.commited = False

    def _del_file(self):
        self.storage.delete(self.url)
        if hasattr(self, '_file'):
            del self._file

        self.url = ''

    file = property(_get_file, _set_file, _del_file)

    def open(self):
        self._get_file()
        return self._file

    def save(self):
        if not self.commited:
            name = os.path.join(self.field.upload_to,
                                os.path.basename(self._file.name))
            self.storage.save(name, self._file)
            self.commited = True

    def delete(self):
        self._del_file()


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
        return S3File(value, self)

    def to_python(self, value):
        if value is None or isinstance(value, S3File):
            return value

        return S3File(value, self)
