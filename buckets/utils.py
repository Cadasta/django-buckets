from django.conf import settings


def validate_settings():
    assert settings.AWS, \
        "No AWS settings found"
    assert settings.AWS.get('ACCESS_KEY'), \
        "AWS access key is not set in settings"
    assert settings.AWS.get('SECRET_KEY'), \
        "AWS secret key is not set in settings"
    assert settings.AWS.get('BUCKET'), \
        "AWS bucket name is not set in settings"
