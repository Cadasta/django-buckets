import os
from django.conf import settings

from tests.mocks import FakeS3Storage, create_file, make_dirs  # noqa


def test_open(make_dirs):  # noqa
    file = create_file()
    with open(os.path.join(settings.MEDIA_ROOT,
              'uploads', 'text.txt'), 'wb') as dest_file:
        dest_file.write(open(file.name, 'rb').read())

    store = FakeS3Storage()
    downloaded = store.open('/media/uploads/text.txt')
    assert downloaded.read().decode() == 'Some content'
    assert os.path.isfile(os.path.join(os.getcwd(),
                          'tests/files/downloads/text.txt'))


def test_save(make_dirs):  # noqa
    file = create_file()
    store = FakeS3Storage()
    url = store.save('uploads/text.txt', file)

    assert url == '/media/uploads/text.txt'
    assert os.path.isfile(os.path.join(os.getcwd(),
                          'tests/files/uploads/text.txt'))


def test_delete(make_dirs):  # noqa
    file = create_file()
    with open(os.path.join(settings.MEDIA_ROOT,
              'uploads', 'text.txt'), 'wb') as dest_file:
        dest_file.write(open(file.name, 'rb').read())

    store = FakeS3Storage()
    store.delete('/media/uploads/text.txt')
    assert not os.path.isfile(os.path.join(os.getcwd(),
                              'tests/files/uploads/text.txt'))
