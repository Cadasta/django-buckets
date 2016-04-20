import pytest
import shutil
import os

from django.conf import settings


def ensure_dirs():
    path = os.path.join(settings.MEDIA_ROOT, 'uploads')
    if not os.path.exists(path):
        os.makedirs(path)

    path = os.path.join(settings.MEDIA_ROOT, 'downloads')
    if not os.path.exists(path):
        os.makedirs(path)


@pytest.fixture(scope='function')
def make_dirs(request):
    ensure_dirs()

    def teardown():
        shutil.rmtree(settings.MEDIA_ROOT)
    request.addfinalizer(teardown)


def create_file():
    path = os.path.join(settings.MEDIA_ROOT, 'text.txt')
    file = open(path, 'wb')
    file.write('Some content'.encode('utf-8'))
    file.close()

    return file
