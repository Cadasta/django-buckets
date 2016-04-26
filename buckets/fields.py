import os
from django.utils.translation import ugettext as _
from django.core.files.storage import default_storage
from django.db import models

from .widgets import S3FileUploadWidget


class S3File(object):
    """ This is the internal value an `S3FileField`. It provides access to the
        actual file on S3, e.g. for post-processing. It usually uses an
        instance of S3Storage to download, upload or delete the file on S3."""
    def __init__(self, url, field):
        self.field = field
        self.storage = field.storage
        self.url = url
        self.committed = True

    def _get_file(self):
        if not hasattr(self, '_file') or not self._file:
            path = self.storage.open(self.url)
            self._file = open(path, 'rb')
        return self._file

    def _set_file(self, file):
        self._file = file
        self.committed = False

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
        if not self.committed:
            name = os.path.join(self.field.upload_to,
                                os.path.basename(self._file.name))
            self.url = self.storage.save(name, self._file)
            self.committed = True

        return self.url

    def delete(self):
        self._del_file()


class S3FileDescriptor(object):
    def __init__(self, field):
        self.field = field

    def __get__(self, instance, value):
        return instance.__dict__[self.field.name]

    def __set__(self, instance, value):
        if isinstance(value, S3File):
            instance.__dict__[self.field.name] = value
        else:
            instance.__dict__[self.field.name] = S3File(value, self.field)


class S3FileField(models.Field):
    """ Stores and provides access to a file stored in an AWS S3 bucket. To set
        the value of an `S3FileField` you usually provide the URL of the file
        in the bucket. Internally this URL is converted to a `S3File`, which
        provides access to the actual file on S3."""
    attr_class = S3File
    descriptor_class = S3FileDescriptor

    description = _("A file stored in an AWS S3 buckets.")

    def __init__(self, upload_to='', storage=None, *args, **kwargs):
        self.storage = storage or default_storage
        self.upload_to = upload_to
        self.widget = S3FileUploadWidget(upload_to=upload_to)

        kwargs['max_length'] = kwargs.get('max_length', 200)
        super(S3FileField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'CharField'

    def contribute_to_class(self, cls, name, **kwargs):
        super(S3FileField, self).contribute_to_class(cls, name, **kwargs)
        setattr(cls, self.name, self.descriptor_class(self))

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

    def get_prep_value(self, value):
        if isinstance(value, S3File):
            return value.url

        return value

    def pre_save(self, model_instance, add):
        file = getattr(model_instance, self.name)
        file.save()

        return file.url

    def formfield(self, *args, **kwargs):
        kwargs['widget'] = self.widget
        return super(S3FileField, self).formfield(*args, **kwargs)
