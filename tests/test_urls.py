try:
    from django.core.urlresolvers import reverse, resolve
except ImportError:
    from django.urls import reverse, resolve
from buckets.views import signed_url


def test_signed_url():
    assert reverse('s3_signed_url') == '/s3/signed-url/'
    assert resolve('/s3/signed-url/').func == signed_url
