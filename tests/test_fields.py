import os
import pytest

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from buckets.fields import S3File, S3FileField, key_from_url
from buckets.widgets import S3FileUploadWidget
from buckets.test.mocks import create_file, make_dirs  # noqa
from buckets.test.storage import FakeS3Storage
from .models import FileModel


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
              's3/uploads/files/text.txt'), 'wb') as dest_file:
        dest_file.write(open(file.name, 'rb').read())

    field = S3FileField(upload_to='files', storage=FakeS3Storage())

    s3_file = S3File('/media/s3/uploads/files/text.txt', field)
    downloaded = s3_file.open()

    assert downloaded.read().decode() == 'Some content'
    assert os.path.isfile(
        os.path.join(settings.MEDIA_ROOT, 's3/uploads/files/text.txt'))


def test_set_file_and_save(make_dirs):   # noqa
    field = S3FileField(storage=FakeS3Storage())
    s3_file = S3File('/media/s3/uploads/text.txt', field)
    s3_file.file = SimpleUploadedFile(
        'text.txt', open(create_file().name, 'rb').read())
    assert s3_file.committed is False
    url = s3_file.save()

    assert url == '/media/s3/uploads/text.txt'
    assert s3_file.committed is True
    assert os.path.isfile(
        os.path.join(settings.MEDIA_ROOT, 's3', 'uploads', 'text.txt'))


def test_delete_file(make_dirs):  # noqa
    file = create_file()
    with open(os.path.join(settings.MEDIA_ROOT,
              's3', 'uploads', 'text.txt'), 'wb') as dest_file:
        dest_file.write(open(file.name, 'rb').read())

    field = S3FileField(storage=FakeS3Storage())

    s3_file = S3File('/media/s3/uploads/text.txt', field)
    s3_file.file = dest_file
    s3_file.delete()

    assert not hasattr(s3_file, '_file')
    assert not os.path.isfile(
        os.path.join(settings.MEDIA_ROOT, 's3', 'uploads', 'text.txt'))


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
    assert field.get_internal_type() == 'CharField'


def test_formfield():
    field = S3FileField()
    form_field = field.formfield()
    assert isinstance(form_field.widget, S3FileUploadWidget)


def test_formfield_with_kwargs():
    field = S3FileField(upload_to='test', accepted_types=['image/png'])
    form_field = field.formfield()
    assert isinstance(form_field.widget, S3FileUploadWidget)
    assert form_field.widget.upload_to == 'test'
    assert form_field.widget.accepted_types == ['image/png']


@pytest.mark.django_db
def test_save_with_url():
    m = FileModel.objects.create(s3_file='http://example.com')
    assert isinstance(m.s3_file, S3File)
    assert m.s3_file.url == 'http://example.com'


@pytest.mark.django_db
def test_save_with_file():
    file = S3File('/someurl/text.txt', S3FileField())
    m = FileModel.objects.create(s3_file=file)
    assert m.s3_file is file


def test_pre_save():
    model_instance = FileModel(
        s3_file='http://example.com'
    )
    field = S3FileField(name='s3_file')
    field._original_url = 'http://example.com'
    url = field.pre_save(model_instance, False)

    assert url == 'http://example.com'


@pytest.mark.django_db
def test_pre_save_replace_file():
    file = create_file()
    with open(os.path.join(settings.MEDIA_ROOT,
              's3/uploads/text.txt'), 'wb') as dest_file:
        dest_file.write(open(file.name, 'rb').read())
    with open(os.path.join(settings.MEDIA_ROOT,
              's3/uploads/text2.txt'), 'wb') as dest_file:
        dest_file.write(open(file.name, 'rb').read())

    model_instance = FileModel(s3_file='/media/s3/uploads/text.txt')
    model_instance.save()
    model_instance.refresh_from_db()

    field = model_instance.s3_file.field
    field.storage = FakeS3Storage()
    model_instance.s3_file = '/media/s3/uploads/text2.txt'
    url = field.pre_save(model_instance, False)
    assert url == '/media/s3/uploads/text2.txt'
    assert not os.path.isfile(os.path.join(settings.MEDIA_ROOT,
                              's3/uploads/text.txt'))


@pytest.mark.django_db
def test_pre_save_delete_file():
    file = create_file()
    with open(os.path.join(settings.MEDIA_ROOT,
              's3/uploads/text.txt'), 'wb') as dest_file:
        dest_file.write(open(file.name, 'rb').read())

    model_instance = FileModel(s3_file='/media/s3/uploads/text.txt')
    model_instance.save()
    model_instance.refresh_from_db()

    field = model_instance.s3_file.field
    field.storage = FakeS3Storage()
    model_instance.s3_file = ''
    url = field.pre_save(model_instance, False)
    assert url == ''
    assert not os.path.isfile(os.path.join(settings.MEDIA_ROOT,
                              's3/uploads/text.txt'))


def test_key_from_url():
    assert (key_from_url('http://example.com/some/dir/file.txt', None) ==
            'file.txt')
    assert (key_from_url('http://example.com/some/dir/file.txt', 'some/dir') ==
            'some/dir/file.txt')
