from django.conf import settings

import boto3
from botocore.client import Config

from buckets.storage import S3Storage
from buckets.test.mocks import create_file, make_dirs  # noqa


def get_boto_resource(storage):
    return boto3.resource(
        's3',
        aws_access_key_id=storage.access_key,
        aws_secret_access_key=storage.secret_key,
        region_name=storage.region,
        config=Config(signature_version='s3v4')
    )


def test_get_signed_url():
    bucket_name = settings.AWS.get('BUCKET')
    storage = S3Storage()

    signed = storage.get_signed_url(key='file.txt')
    assert ('https://s3.amazonaws.com/{}'.format(bucket_name) == signed['url'])
    assert len(signed['fields']['key']) == 28


def test_get_signed_url_with_subdir():
    bucket_name = settings.AWS.get('BUCKET')
    storage = S3Storage()

    signed = storage.get_signed_url(key='subdir/file.txt')

    assert ('https://s3.amazonaws.com/{}'.format(bucket_name) == signed['url'])
    assert len(signed['fields']['key']) == 35


def test_get_file(make_dirs):  # noqa
    txt = create_file()
    file = open(txt.name, 'rb')

    storage = S3Storage()
    s3 = get_boto_resource(storage)
    s3.Object(storage.bucket_name, 'test/uploaded.txt').put(Body=file)

    file = storage.open('test/uploaded.txt')
    assert open(file, 'rb').read().decode() == "Some content"


def test_upload_file(make_dirs):  # noqa
    txt = create_file()
    file = open(txt.name, 'rb')

    storage = S3Storage()
    url = storage.save('test/text.txt', file)
    name = url.split('/')[-1]

    s3 = get_boto_resource(storage)
    o = s3.Object(storage.bucket_name, 'test/' + name).get()
    assert("Some content" in o['Body'].read(o['ContentLength']).decode())
