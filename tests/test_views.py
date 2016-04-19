import pytest
import json

from django.http import HttpRequest
from django.core.files.storage import FileSystemStorage

from buckets import views, exceptions


def test_validate_valid_payload():
    post_payload = {
        'client_method': 'get_object',
        'http_method': 'GET'
    }
    views.validate_payload(post_payload)


def test_validate_empty_payload():
    post_payload = {}
    with pytest.raises(exceptions.InvalidPayload) as e:
        views.validate_payload(post_payload)

    assert ("'http_method' is required" in e.value.errors['http_method'])
    assert ("'client_method' is required" in e.value.errors['client_method'])


def test_validate_invalid_payload():
    post_payload = {
        'client_method': 'patch_object',
        'http_method': 'patch'
    }
    with pytest.raises(exceptions.InvalidPayload) as e:
        views.validate_payload(post_payload)

    assert ("'http_method' must be one of get, put, delete" in
            e.value.errors['http_method'])
    assert ("'client_method' must be one of get_object, put_object, "
            "delete_object" in e.value.errors['client_method'])


def test_get_signed_url():
    """View should reply with error code 405 because only POST is allowed as
       request method"""
    request = HttpRequest()
    setattr(request, 'method', 'GET')

    response = views.signed_url(request)
    assert response.status_code == 405


def test_post_signed_url_with_valid_payload():
    """View should reply with error code 200 and a signed AWS URL"""
    post_payload = {
        'client_method': 'get_object',
        'http_method': 'GET'
    }

    request = HttpRequest()
    setattr(request, 'method', 'POST')
    setattr(request, 'POST', post_payload)

    response = views.signed_url(request)
    content = response.content.decode('utf-8')

    assert response.status_code == 200
    assert 'signed_url' in json.loads(content)


def test_post_signed_url_where_not_supported(monkeypatch):
    monkeypatch.setattr(views, 'default_storage', FileSystemStorage())

    post_payload = {
        'client_method': 'get_object',
        'http_method': 'GET'
    }

    request = HttpRequest()
    setattr(request, 'method', 'POST')
    setattr(request, 'POST', post_payload)

    response = views.signed_url(request)
    content = response.content.decode('utf-8')

    assert response.status_code == 404
    assert json.loads(content)['error'] == "Not found"


def test_post_signed_url_with_invalid_payload():
    post_payload = {
        'client_method': 'get_object',
    }

    request = HttpRequest()
    setattr(request, 'method', 'POST')
    setattr(request, 'POST', post_payload)

    response = views.signed_url(request)
    content = response.content.decode('utf-8')

    assert response.status_code == 400
    assert 'http_method' in json.loads(content)
