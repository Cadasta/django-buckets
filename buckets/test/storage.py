import os
import urllib

from django.conf import settings


class FakeS3Storage(object):
    def __init__(self, dir=None):
        self.dir = dir or settings.MEDIA_ROOT

    def open(self, url):
        name = os.path.basename(urllib.request.url2pathname(url))
        uploaded = os.path.join(self.dir, 'uploads', name)

        with open(os.path.join(self.dir, 'downloads', name), 'wb') as dest:
            dest.write(open(uploaded, 'rb').read())
            dest.close()

        return open(dest.name, 'rb')

    def save(self, name, content):
        url = '/media/' + name

        with open(os.path.join(self.dir, name), 'wb') as dest:
            dest.write(content.read())
            dest.close()

        return url

    def delete(self, url):
        name = os.path.basename(urllib.request.url2pathname(url))
        uploaded = os.path.join(self.dir, 'uploads', name)
        os.remove(uploaded)

    def get_signed_url(self, client_method=None, http_method=None):
        return '/s3/files/'
