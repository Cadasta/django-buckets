import pytest
from buckets.fields import S3File, S3FileField

# #############################################################################
#
# S3File
#
# #############################################################################


def test_initialization():
    file = S3File(url='https://example.com/test.text')
    assert file.url == 'https://example.com/test.text'


def test_initialization_without_url():
    with pytest.raises(AssertionError) as e:
        S3File()
    assert e.value.msg == "Cannot initialize S3File, url not set"


# #############################################################################
#
# S3FileField
#
# #############################################################################


class FakeStorage(object):
    pass


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
                        storage=FakeStorage,
                        max_length=400)
    name, path, args, kwargs = field.deconstruct()

    assert name is None
    assert path == 'buckets.fields.S3FileField'
    assert args == []

    assert kwargs['max_length'] == 400
    assert kwargs['upload_to'] == '/uploads/'
    assert kwargs['storage'] == FakeStorage


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
    file = S3File(url='https://example.com/test.text')
    field = S3FileField()
    python_obj = field.to_python(file)
    assert python_obj is file


def test_to_python_with_url():
    field = S3FileField()
    python_obj = field.to_python('https://example.com/test.text')
    assert isinstance(python_obj, S3File)
    assert python_obj.url == 'https://example.com/test.text'
