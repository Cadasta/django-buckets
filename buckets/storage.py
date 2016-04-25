import os
from django.conf import settings
from django.core.files.storage import Storage

import boto3
from botocore.client import Config

from .utils import validate_settings


class S3Storage(Storage):
    def __init__(self):
        validate_settings()

        self.access_key = settings.AWS['ACCESS_KEY']
        self.secret_key = settings.AWS['SECRET_KEY']
        self.bucket_name = settings.AWS['BUCKET']

    def get_boto_ressource(self):
        return boto3.resource(
            's3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(signature_version='s3v4')
        )

    def _open(self, name, mode='rb'):
        s3 = self.get_boto_ressource()
        f = s3.Object(self.bucket_name, name).get()
        write_path = os.path.join(settings.MEDIA_ROOT,
                                  's3/downloads',
                                  name.split('/')[-1])

        with open(write_path, 'wb') as w:
            to_read = True
            body = f['Body']
            while to_read:
                chunk = body.read(1024)
                if chunk:
                    w.write(chunk)
                else:
                    to_read = False

        return w.name

    def _save(self, name, content):
        s3 = self.get_boto_ressource()
        s3.Object(self.bucket_name, name).put(Body=content)

        return 'https://s3.amazonaws.com/{}/{}'.format(self.bucket_name, name)

    def get_available_name(self, name, max_length=None):
        return name

    def get_valid_name(self, name):
        return name

    def get_signed_url(self, key=None):
        params = {
            'Bucket': self.bucket_name,
            'Key': key
        }

        client = boto3.client(
            's3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(signature_version='s3v4')
        )

        return client.generate_presigned_post(**params)
