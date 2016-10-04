import os
import pytest
import json

from django.conf import settings
from django.http import HttpRequest
from django.core.files.storage import FileSystemStorage

from buckets import views, exceptions
from buckets.test.storage import FakeS3Storage
from buckets.test.mocks import create_file, make_dirs  # noqa


def test_validate_valid_payload():
    post_payload = {'key': 'file.txt'}
    views.validate_payload(post_payload)


def test_validate_empty_payload():
    post_payload = {}
    with pytest.raises(exceptions.InvalidPayload) as e:
        views.validate_payload(post_payload)

    assert ("'key' is required" in e.value.errors['key'])


def test_get_signed_url():
    """View should reply with error code 405 because only POST is allowed as
       request method"""
    request = HttpRequest()
    setattr(request, 'method', 'GET')

    response = views.signed_url(request)
    assert response.status_code == 405


def test_post_signed_url_with_valid_payload():
    """View should reply with error code 200 and a signed AWS URL"""
    post_payload = {'key': 'file.txt'}

    request = HttpRequest()
    setattr(request, 'method', 'POST')
    setattr(request, 'POST', post_payload)

    response = views.signed_url(request)
    content = response.content.decode('utf-8')

    assert response.status_code == 200
    assert 'url' in json.loads(content)


def test_post_signed_url_where_not_supported(monkeypatch):
    monkeypatch.setattr(views, 'default_storage', FileSystemStorage())

    post_payload = {'key': 'file.txt'}

    request = HttpRequest()
    setattr(request, 'method', 'POST')
    setattr(request, 'POST', post_payload)

    response = views.signed_url(request)
    content = response.content.decode('utf-8')

    assert response.status_code == 404
    assert json.loads(content)['error'] == "Not found"


def test_post_signed_url_with_invalid_payload():
    post_payload = {}

    request = HttpRequest()
    setattr(request, 'method', 'POST')
    setattr(request, 'POST', post_payload)

    response = views.signed_url(request)
    content = response.content.decode('utf-8')

    assert response.status_code == 400
    assert 'key' in json.loads(content)


def test_delete_resource(make_dirs, monkeypatch):  # noqa
    monkeypatch.setattr(views, 'default_storage', FakeS3Storage())
    create_file(subdir='uploads', name='delete.txt')

    request = HttpRequest()
    setattr(request, 'method', 'POST')
    setattr(request, 'POST', {'key': 'delete.txt'})
    response = views.delete_resource(request)
    assert response.status_code == 204
    assert not os.path.isfile(
        os.path.join(settings.MEDIA_ROOT, 's3,' 'uploads', 'delete.txt'))


def test_delete_non_existing_resource(make_dirs, monkeypatch):  # noqa
    monkeypatch.setattr(views, 'default_storage', FakeS3Storage())

    request = HttpRequest()
    setattr(request, 'method', 'POST')
    setattr(request, 'POST', {'key': 'delete.txt'})
    response = views.delete_resource(request)
    content = json.loads(response.content.decode('utf-8'))
    assert response.status_code == 400
    assert content['error'] == 'S3 resource does not exist.'
