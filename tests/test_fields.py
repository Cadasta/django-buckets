import os

from django.conf import settings
from django.db import models

from buckets.fields import S3File, S3FileField
from buckets.widgets import S3FileUploadWidget
from .mocks import FakeS3Storage, create_file, make_dirs  # noqa


#############################################################################

# S3File

#############################################################################

def test_init():
    field = S3FileField(storage=FakeS3Storage())
    file = S3File('https://example.com/text.txt', field)

    assert file.url == 'https://example.com/text.txt'
    assert file.field is field
    assert isinstance(file.storage, FakeS3Storage)


def test_get_file(make_dirs):  # noqa
    file = create_file()
    with open(os.path.join(settings.MEDIA_ROOT,
              'uploads', 'text.txt'), 'wb') as dest_file:
        dest_file.write(open(file.name, 'rb').read())

    field = S3FileField(upload_to='uploads', storage=FakeS3Storage())

    s3_file = S3File('/media/uploads/text.txt', field)
    downloaded = s3_file.open()

    assert downloaded.read().decode() == 'Some content'
    assert os.path.isfile(os.path.join(os.getcwd(),
                                       'tests/files/downloads/text.txt'))


def test_set_file_and_save(make_dirs):   # noqa
    field = S3FileField(upload_to='uploads', storage=FakeS3Storage())
    s3_file = S3File('/media/uploads/text.txt', field)
    s3_file.file = create_file()
    assert s3_file.committed is False
    url = s3_file.save()

    assert url == '/media/uploads/text.txt'
    assert s3_file.committed is True
    assert os.path.isfile(os.path.join(os.getcwd(),
                                       'tests/files/uploads/text.txt'))


def test_delete_file(make_dirs):  # noqa
    file = create_file()
    with open(os.path.join(settings.MEDIA_ROOT,
              'uploads', 'text.txt'), 'wb') as dest_file:
        dest_file.write(open(file.name, 'rb').read())

    field = S3FileField(upload_to='uploads', storage=FakeS3Storage())

    s3_file = S3File('/media/uploads/text.txt', field)
    s3_file.file = dest_file
    s3_file.delete()

    assert not hasattr(s3_file, '_file')
    assert not os.path.isfile(os.path.join(os.getcwd(),
                                           'tests/files/uploads/text.txt'))


# #############################################################################
#
# S3FileField
#
# #############################################################################

def test_deconstruct_default_kwargs():
    field = S3FileField()
    name, path, args, kwargs = field.deconstruct()

    assert name is None
    assert path == 'buckets.fields.S3FileField'
    assert args == []

    assert 'max_length' not in kwargs
    assert 'upload_to' not in kwargs
    assert 'storage' not in kwargs


def test_deconstruct_custom_kwargs():
    field = S3FileField(upload_to='/uploads/',
                        storage=FakeS3Storage(),
                        max_length=400)
    name, path, args, kwargs = field.deconstruct()

    assert name is None
    assert path == 'buckets.fields.S3FileField'
    assert args == []

    assert kwargs['max_length'] == 400
    assert kwargs['upload_to'] == '/uploads/'
    assert isinstance(kwargs['storage'], FakeS3Storage)


def test_from_db_value():
    field = S3FileField()
    converted = field.from_db_value('https://example.com/test.text',
                                    None, None, None)
    assert isinstance(converted, S3File)
    assert converted.url == 'https://example.com/test.text'


def test_to_python_with_None():
    field = S3FileField()
    python_obj = field.to_python(None)
    assert python_obj is None


def test_to_python_with_S3File():
    field = S3FileField()
    file = S3File('https://example.com/test.text', field)
    python_obj = field.to_python(file)
    assert python_obj is file


def test_to_python_with_url():
    field = S3FileField()
    python_obj = field.to_python('https://example.com/test.text')
    assert isinstance(python_obj, S3File)
    assert python_obj.url == 'https://example.com/test.text'


def test_get_prep_value():
    field = S3FileField()
    s3_file = S3File('https://example.com/test.text', field)

    url = field.get_prep_value(s3_file)
    assert url == 'https://example.com/test.text'


def test_get_internal_type():
    field = S3FileField()
    assert field.get_internal_type() == 'URLField'


def test_formfield():
    field = S3FileField()
    form_field = field.formfield()
    assert isinstance(form_field.widget, S3FileUploadWidget)


class FileModel(models.Model):
    s3_file = S3FileField()

    class Meta:
        app_label = 'core'


def test_pre_save():
    model_instance = FileModel(
        s3_file='http://example.com'
    )
    field = S3FileField(name='s3_file')
    url = field.pre_save(model_instance, False)

    assert url == 'http://example.com'
