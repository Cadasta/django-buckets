import pytest
import shutil
import os

from django.conf import settings

from buckets.utils import ensure_dirs


@pytest.fixture(scope='function')
def make_dirs(request):
    ensure_dirs('uploads', 'downloads', 'uploads/files')

    def teardown():
        shutil.rmtree(os.path.join(settings.MEDIA_ROOT, 's3'))
    request.addfinalizer(teardown)


def create_file(subdir=None, name='text.txt'):
    path = 's3'
    if subdir:
        path += '/' + subdir
    path = os.path.join(settings.MEDIA_ROOT, path, name)
    file = open(path, 'wb')
    file.write('Some content'.encode('utf-8'))
    file.close()

    return file
