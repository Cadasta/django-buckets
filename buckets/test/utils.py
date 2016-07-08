import os
from django.conf import settings


def ensure_dirs(add=None):
    path = os.path.join(settings.MEDIA_ROOT, 's3', 'uploads')
    if not os.path.exists(path):
        os.makedirs(path)

    path = os.path.join(settings.MEDIA_ROOT, 's3', 'downloads')
    if not os.path.exists(path):
        os.makedirs(path)

    if add:
        path = os.path.join(settings.MEDIA_ROOT, add)
        if not os.path.exists(path):
            os.makedirs(path)
