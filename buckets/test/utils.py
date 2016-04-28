import os
from django.conf import settings


def ensure_dirs():
    path = os.path.join(settings.MEDIA_ROOT, 's3', 'uploads')
    if not os.path.exists(path):
        os.makedirs(path)

    path = os.path.join(settings.MEDIA_ROOT, 's3', 'downloads')
    if not os.path.exists(path):
        os.makedirs(path)
