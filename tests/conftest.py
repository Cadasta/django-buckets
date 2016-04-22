

# os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def pytest_configure():
    import os
    from django.conf import settings

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    settings.configure(
        DEBUG_PROPAGATE_EXCEPTIONS=True,
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3',
                               'NAME': ':memory:'}},
        SITE_ID=1,
        SECRET_KEY='not very secret in tests',
        USE_I18N=True,
        USE_L10N=True,
        STATIC_URL='/static/',
        TEMPLATE_LOADERS=(
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ),
        MIDDLEWARE_CLASSES=(
            'django.middleware.common.CommonMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ),
        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',
            'django.contrib.messages',
            'django.contrib.staticfiles',

            'buckets',
            'tests',
            # 'example.exampleapp',
        ),
        DEFAULT_FILE_STORAGE='buckets.storage.S3Storage',
        AWS={
            'BUCKET': os.environ.get('AWS_BUCKET'),
            'ACCESS_KEY': os.environ.get('AWS_ACCESS_KEY'),
            'SECRET_KEY': os.environ.get('AWS_SECRET_KEY'),
        },
        ROOT_URLCONF='buckets.test.urls',
        MEDIA_ROOT=os.path.join(os.path.dirname(BASE_DIR), 'files'),
        MEDIA_URL='/media/',
    )

    try:
        import django
        django.setup()
    except AttributeError:
        pass
