import pytest
import shutil
import os

from django.conf import settings

from .utils import ensure_dirs


@pytest.fixture(scope='function')
def make_dirs(request):
    ensure_dirs()

    def teardown():
        shutil.rmtree(os.path.join(settings.MEDIA_ROOT, 's3'))
    request.addfinalizer(teardown)


def create_file():
    path = os.path.join(settings.MEDIA_ROOT, 's3', 'text.txt')
    file = open(path, 'wb')
    file.write('Some content'.encode('utf-8'))
    file.close()

    return file
