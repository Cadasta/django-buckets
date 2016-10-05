import pytest
import os
from django.conf import settings
from django.core.urlresolvers import reverse, resolve
from django.http import HttpRequest
from django.core.files.uploadedfile import SimpleUploadedFile

from buckets.test.mocks import create_file, make_dirs  # noqa
from buckets.test.storage import FakeS3Storage
from buckets.test import views
from buckets.exceptions import S3ResourceNotFound


#############################################################################

# FakeS3Storage

#############################################################################


def test_open(make_dirs):  # noqa
    file = create_file()
    with open(os.path.join(settings.MEDIA_ROOT,
              's3', 'uploads', 'text.txt'), 'wb') as dest_file:
        dest_file.write(open(file.name, 'rb').read())

    store = FakeS3Storage()
    downloaded = store.open('text.txt')
    assert open(downloaded, 'rb').read().decode() == 'Some content'
    assert os.path.isfile(
        os.path.join(settings.MEDIA_ROOT, 's3', 'uploads', 'text.txt'))


def test_save(make_dirs):  # noqa
    file = create_file()
    store = FakeS3Storage()
    url = store.save('text.txt', open(file.name, 'rb').read())

    assert url == '/media/s3/uploads/text.txt'
    assert os.path.isfile(
        os.path.join(settings.MEDIA_ROOT, 's3', 'uploads', 'text.txt'))


def test_save_with_subdir(make_dirs):  # noqa
    file = create_file()
    store = FakeS3Storage()
    url = store.save('somedir/text.txt', open(file.name, 'rb').read())

    assert url == '/media/s3/uploads/somedir/text.txt'
    assert os.path.isfile(
        os.path.join(settings.MEDIA_ROOT, 's3/uploads/somedir/text.txt'))


def test_delete(make_dirs):  # noqa
    file = create_file()
    with open(os.path.join(settings.MEDIA_ROOT,
              's3', 'uploads', 'delete.txt'), 'wb') as dest_file:
        dest_file.write(open(file.name, 'rb').read())

    store = FakeS3Storage()
    store.delete('delete.txt')
    assert not os.path.isfile(
        os.path.join(settings.MEDIA_ROOT, 's3,' 'uploads', 'text.txt'))


def test_delete_non_exising_file(make_dirs):  # noqa
    store = FakeS3Storage()
    with pytest.raises(S3ResourceNotFound):
        store.delete('/media/s3/uploads/delete.txt')


def test_get_signed_url():
    store = FakeS3Storage()

    signed = store.get_signed_url(key='file.txt')
    assert '/media/s3/uploads' == signed['url']
    assert len(signed['fields']['key']) == 28


def test_content_via_save(make_dirs):  # noqa
    store = FakeS3Storage()
    txt = 'blah'
    content = str.encode(txt)
    url = store.save('blah.txt', content)
    assert url == '/media/s3/uploads/blah.txt'


#############################################################################

# URLs

#############################################################################


def test_urls():
    assert reverse('fake_s3_upload') == '/media/s3/uploads'

    resolved = resolve('/media/s3/uploads')
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
    setattr(request, 'POST', {
        'key': 'text.txt'
    })
    response = views.fake_s3_upload(request)
    assert response.status_code == 204
    assert os.path.isfile(
        os.path.join(settings.MEDIA_ROOT, 's3', 'uploads', 'text.txt'))


def test_post_upload_file_to_subdir(make_dirs, monkeypatch):  # noqa
    monkeypatch.setattr(views, 'default_storage', FakeS3Storage())
    file = create_file()
    request = HttpRequest()
    setattr(request, 'method', 'POST')
    setattr(request, 'FILES', {
        'file': SimpleUploadedFile('text.txt', open(file.name, 'rb').read())
    })
    setattr(request, 'POST', {
        'key': 'subdir/text.txt'
    })
    response = views.fake_s3_upload(request)
    assert response.status_code == 204
    assert os.path.isfile(
        os.path.join(settings.MEDIA_ROOT, 's3/uploads/subdir', 'text.txt'))
