import os
from django.conf import settings
from django.core.files.storage import Storage
from django.core.files import File

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from .utils import validate_settings, random_id, ensure_dirs


class S3Storage(Storage):
    def __init__(self):
        validate_settings()

        self.access_key = settings.AWS['ACCESS_KEY']
        self.secret_key = settings.AWS['SECRET_KEY']
        self.region = settings.AWS['REGION']
        self.bucket_name = settings.AWS['BUCKET']

        ensure_dirs('downloads')

    def get_boto_ressource(self):
        return boto3.resource(
            's3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
            config=Config(signature_version='s3v4')
        )

    def _open(self, name, mode='rb'):
        s3 = self.get_boto_ressource()
        f = s3.Object(self.bucket_name, name).get()
        write_path = os.path.join(settings.MEDIA_ROOT, 's3/downloads',
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
        if isinstance(content, File):
            content = content.file
        s3.Object(self.bucket_name, name).put(Body=content)

        return 'https://s3-{}.amazonaws.com/{}/{}'.format(
            self.region, self.bucket_name, name)

    def delete(self, name):
        s3 = self.get_boto_ressource()
        s3.Object(self.bucket_name, name).delete()

    def exists(self, name):
        s3 = self.get_boto_ressource()
        try:
            s3.Object(self.bucket_name, name).load()
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False
            else:
                raise e
        else:
            return True

    def get_signed_url(self, key=None):
        dir = ''
        if '/' in key:
            dir = key[:key.rfind('/') + 1]

        ext = key[key.rfind('.'):]
        s3_key = ''

        while not s3_key:
            temp_key = dir + random_id() + ext

            if not self.exists(temp_key):
                s3_key = temp_key

        params = {
            'Bucket': self.bucket_name,
            'Key': s3_key
        }
        client = boto3.client(
            's3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
            config=Config(signature_version='s3v4')
        )

        return client.generate_presigned_post(**params)
