import os
import urllib

from django.conf import settings


class FakeS3Storage(object):
    def __init__(self, dir=None):
        self.dir = dir or os.path.join(settings.MEDIA_ROOT, 's3')

    def open(self, url):
        name = os.path.basename(urllib.request.url2pathname(url))
        uploaded = os.path.join(self.dir, 'uploads', name)

        with open(os.path.join(self.dir, 'downloads', name), 'wb') as dest:
            dest.write(open(uploaded, 'rb').read())
            dest.close()

        return dest.name

    def save(self, name, content):
        url = '/media/s3/uploads/' + name

        with open(os.path.join(self.dir, 'uploads', name), 'wb') as dest:
            dest.write(content.read())

        return url

    def delete(self, url):
        name = os.path.basename(urllib.request.url2pathname(url))
        uploaded = os.path.join(self.dir, 'uploads', name)
        os.remove(uploaded)

    def get_signed_url(self, key=None):
        return {'url': '/media/s3/uploads', 'fields': {'key': key}}
