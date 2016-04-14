import boto3
from botocore.client import Config
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


def get_signed_url(client_method='get_object', http_method='GET'):
    validate_settings()

    params = {
        'Bucket': settings.AWS['BUCKET'],
        'Key': settings.AWS['ACCESS_KEY']
    }

    client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS['ACCESS_KEY'],
        aws_secret_access_key=settings.AWS['SECRET_KEY'],
        config=Config(signature_version='s3v4')
    )
    signed = client.generate_presigned_url(
        ClientMethod=client_method,
        Params=params,
        ExpiresIn=3600,
        HttpMethod=http_method
    )

    return signed
