from django.core.urlresolvers import reverse, resolve
from buckets.views import signed_url, delete_resource


def test_signed_url():
    assert reverse('s3_signed_url') == '/s3/signed-url/'
    assert resolve('/s3/signed-url/').func == signed_url


def test_delete_resource():
    assert reverse('s3_delete_resource') == '/s3/delete-resource/'
    assert resolve('/s3/delete-resource/').func == delete_resource
