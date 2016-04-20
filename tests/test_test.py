import os
from django.conf import settings
from django.core.urlresolvers import reverse, resolve
from django.http import HttpRequest
from django.core.files.uploadedfile import SimpleUploadedFile

from buckets.test.mocks import create_file, make_dirs  # noqa
from buckets.test.storage import FakeS3Storage
from buckets.test import views


#############################################################################

# FakeS3Storage

#############################################################################


def test_open(make_dirs):  # noqa
    file = create_file()
    with open(os.path.join(settings.MEDIA_ROOT,
              'uploads', 'text.txt'), 'wb') as dest_file:
        dest_file.write(open(file.name, 'rb').read())

    store = FakeS3Storage()
    downloaded = store.open('/media/uploads/text.txt')
    assert downloaded.read().decode() == 'Some content'
    assert os.path.isfile(
        os.path.join(settings.MEDIA_ROOT, 'uploads', 'text.txt'))


def test_save(make_dirs):  # noqa
    file = create_file()
    store = FakeS3Storage()
    url = store.save(
        'uploads/text.txt',
        SimpleUploadedFile('text.txt', open(file.name, 'rb').read()))

    assert url == '/media/uploads/text.txt'
    assert os.path.isfile(
        os.path.join(settings.MEDIA_ROOT, 'uploads', 'text.txt'))


def test_delete(make_dirs):  # noqa
    file = create_file()
    with open(os.path.join(settings.MEDIA_ROOT,
              'uploads', 'text.txt'), 'wb') as dest_file:
        dest_file.write(open(file.name, 'rb').read())

    store = FakeS3Storage()
    store.delete('/media/uploads/text.txt')
    assert not os.path.isfile(
        os.path.join(settings.MEDIA_ROOT, 'uploads', 'text.txt'))


#############################################################################

# URLs

#############################################################################


def test_urls():
    assert reverse('fake_s3_upload') == '/s3/files/'

    resolved = resolve('/s3/files/')
    assert resolved.func.__name__ == views.fake_s3_upload.__name__


#############################################################################

# fake_s3_upload

#############################################################################

def test_get_upload_file():
    request = HttpRequest()
    setattr(request, 'method', 'GET')

    response = views.fake_s3_upload(request)
    assert response.status_code == 405


def test_post_upload_file(make_dirs, monkeypatch):  # noqa
    monkeypatch.setattr(views, 'default_storage', FakeS3Storage())
    file = create_file()
    request = HttpRequest()
    setattr(request, 'method', 'POST')
    setattr(request, 'FILES', {
        'file': SimpleUploadedFile('text.txt', open(file.name, 'rb').read())
    })

    response = views.fake_s3_upload(request)
    assert response.status_code == 201
    assert os.path.isfile(
        os.path.join(settings.MEDIA_ROOT, 'uploads', 'text.txt'))
