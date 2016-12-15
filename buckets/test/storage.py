import os
import urllib

from django.conf import settings
from buckets.utils import ensure_dirs, random_id


class FakeS3Storage(object):
    def __init__(self, dir=None):
        self.dir = dir or os.path.join(settings.MEDIA_ROOT, 's3')

        ensure_dirs('downloads', 'uploads')

    def open(self, url):
        name = os.path.basename(urllib.request.url2pathname(url))
        uploaded = os.path.join(self.dir, 'uploads', url)

        with open(os.path.join(self.dir, 'downloads', name), 'wb') as dest:
            dest.write(open(uploaded, 'rb').read())
            dest.close()

        return dest.name

    def save(self, name, content):
        url = '/media/s3/uploads/' + name

        if '/' in name:
            path = os.path.join(settings.MEDIA_ROOT,
                                's3/uploads', name[:name.rfind('/')])
            if not os.path.exists(path):
                os.makedirs(path)

        with open(os.path.join(self.dir, 'uploads', name), 'wb') as dest:
            dest.write(content)

        return url

    def delete(self, name):
        uploaded = os.path.join(self.dir, 'uploads', name)
        try:
            os.remove(uploaded)
        except FileNotFoundError:
            pass

    def exists(self, key):
        path = os.path.join(self.dir, 'uploads', key)
        return os.path.exists(path)

    def get_signed_url(self, key=None):
        dir = ''
        if '/' in key:
            dir = key[:key.rfind('/') + 1]

        ext = key[key.rfind('.'):]
        s3_key = ''

        while not s3_key:
            temp_key = dir + random_id() + ext

            if not self.exists(temp_key):
                s3_key = temp_key

        return {'url': '/media/s3/uploads', 'fields': {'key': s3_key}}
