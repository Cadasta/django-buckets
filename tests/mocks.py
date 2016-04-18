import pytest
import shutil
import os
import urllib

from django.conf import settings


@pytest.fixture(scope='function')
def make_dirs(request):
    path = os.path.join(settings.MEDIA_ROOT, 'uploads')
    if not os.path.exists(path):
        os.makedirs(path)

    path = os.path.join(settings.MEDIA_ROOT, 'downloads')
    if not os.path.exists(path):
        os.makedirs(path)

    def teardown():
        shutil.rmtree(settings.MEDIA_ROOT)
    request.addfinalizer(teardown)


def create_file():
    path = os.path.join(os.getcwd(), 'tests/files/text.txt')
    file = open(path, 'wb')
    file.write('Some content'.encode('utf-8'))
    file.close()

    return file


class FakeS3Storage(object):
    def __init__(self, dir=None):
        self.dir = dir or settings.MEDIA_ROOT

    def open(self, url):
        name = os.path.basename(urllib.request.url2pathname(url))
        uploaded = os.path.join(self.dir, 'uploads', name)

        with open(os.path.join(self.dir, 'downloads', name), 'wb') as dest_file:
            dest_file.write(open(uploaded, 'rb').read())
            dest_file.close()

        return open(dest_file.name, 'rb')

    def save(self, name, content):
        url = '/media/' + name

        with open(os.path.join(self.dir, name), 'wb') as dest_file:
            dest_file.write(open(content.name, 'rb').read())
            dest_file.close()

        return url

    def delete(self, url):
        name = os.path.basename(urllib.request.url2pathname(url))
        uploaded = os.path.join(self.dir, 'uploads', name)
        os.remove(uploaded)
