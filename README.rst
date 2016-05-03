django-buckets
===============================================================================

|pypi-version| |build-status-image|

django-buckets provides a Django storage system (:code:`S3Storage`) to store files on 
`Amazon S3 <https://aws.amazon.com/s3/>`_. Besides the storage itself, the 
library comes with a custom model field (:code:`S3FileField`) to reference 
files in Django and a form widget that handles uploading files to S3 using 
`pre-signed URLs <http://docs.aws.amazon.com/AmazonS3/latest/dev/PresignedUrlUploadObject.html>`_.

For testing and development, django-buckets offers :code:`S3FakeStorage` and
the API endpoint :code:`/media/s3/uploads`, which mimick the behaviour of
:code:`S3Storage` and AWS S3's file upload API but use the local file system. 
Both integrate seamlessly with :code:`S3FileField`.

**django-buckets is work in progress and not stable. Things might break.**

Requirements
-------------------------------------------------------------------------------
- Python 3.4 or 3.5
- Django 1.8 or 1.9

Setup
-------------------------------------------------------------------------------

Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block::

  pip install django-buckets

For production
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In settings, add :code:`buckets` to installed apps, set :code:`S3Storage` as 
default default storage and add the S3 bucket name as well as the AWS access 
key and secret key.

.. code-block:: python

  INSTALLED_APPS = (
    ...
    'buckets',
  )

  DEFAULT_FILE_STORAGE = 'buckets.storage.S3Storage'

  AWS = {
    'BUCKET': 'some-bucket',
    'ACCESS_KEY': 'J36RZO0MO9JQ6NWAOY2I',
    'SECRET_KEY': 'EaANd90ZdgiykkXEf67fNRnhc96zcGnkgDhagj6v',
  }

Include django-buckets' URLs. This will add an `API endpoint <#api>`_, which is
used by the form widget or REST-clients to request valid signed URLs.

.. code-block:: python

  urlpatterns = [
      url(r'', include('buckets.urls')),
  ]

Edit the CORS's policy of the S3 bucket you intend to use to allow for POST
requests:

.. code-block:: xml

  <CORSConfiguration>
    <CORSRule>
        <AllowedOrigin>*</AllowedOrigin>
        <AllowedMethod>POST</AllowedMethod>
        <AllowedMethod>GET</AllowedMethod>
        <MaxAgeSeconds>3000</MaxAgeSeconds>
        <AllowedHeader>*</AllowedHeader>
    </CORSRule>
  </CORSConfiguration>

For testing and development
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In settings, In settings, add :code:`buckets` to installed apps and set
:code:`S3Storage` as default default storage.

.. code-block:: python

 DEFAULT_FILE_STORAGE = 'buckets.test.storage.FakeS3Storage'

Include django-buckets' URLs. This will add an `API endpoint <#api>`_, which is
used by the form widget or REST-clients to request valid signed URLs. Further,
it will add a file upload endpoint, which behaves like S3's file upload but
stores files on the local file system.

.. code-block:: python

  INSTALLED_APPS = (
    ...
    'buckets',
  )

  urlpatterns = [
      url(r'', include('buckets.test.urls')),
  ]

Usage
-------------------------------------------------------------------------------

Create a model class, which has a :code:`S3FileField`. Internally, S3FileField
is a Django `CharField <https://docs.djangoproject.com/en/1.9/ref/models/fields/#charfield>`_
and it accepts the same arguments. In addition, you can provide a value for 
:code:`upload_to` to set an upload directory (just like
`FileField <https://docs.djangoproject.com/en/1.9/ref/models/fields/#filefield>`_).

.. code-block:: python

  from django.db import models
  from buckets.fields import S3FileField

  class MyModel(models.Model):
      name = models.CharField(max_length=200)
      file = S3FileField()


Instanciate the model with an S3 URL:

.. code-block:: python

  file_model = MyModel.objects.create(
      name='My File',
      file='https://s3.amazonaws.com/some-bucket/...'
  )

Internally, an instance of :code:`S3File` is created from the URL that provides
access to the file itself. 

.. code-block:: python

  # downloads the file and returns a File object
  file = file_model.file 

  # assign an updated file
  file_model.file = file

To use the form widget provided by :code:`S3FileField`, add the JavaScript and
CSS to the template's head.

.. code-block:: html

  <html>
    <head>
      <meta charset="utf-8">
      <title>django-buckets File Upload</title>
      {{ form.media }}
    </head>
    <body>
      {{ form.as_p }}
    </body>
  </html>


API
-------------------------------------------------------------------------------

If you are building an API-only application, you can get a signed URL by
POSTing :code:`client_method` and :code:`http_method`.

Request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block::

  POST /s3/signed-url/
  Accept: application/json
  Content-Type: application/json

  {
    "key": "file.txt"
  }

Response
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block::

  HTTP/1.1 200 OK
  Content-Type: application/json

  {
    "url": "https://s3.amazonaws.com/some-bucket", 
    "fields": {
      "key": "file.txt",
      "x-amz-credential": "HKJXXOZ7L71OMC9S830I/20160425/us-east-1/s3/aws4_request",
      "policy": "AORKx5gcfIIMJQUyKAkdCUDapV99I8PAn592rjN2of6Hodk1HNiFrj1ItWdJpuQiwrYVi0NJMnfCxfmfVlZg9NDpKFQi8b5vSpWpamMu5UVUdg9c8A77lF1fuWOty8Xx4qUza8EXxuz49mYYRhRym8TRNzx4v9qDwPmILe6FRl7BGSlIijn46Td9OroAHJoUPp2YU1dwsGOXGZufCGHJ8C3m1vM0YmPhDTvt2WABGscgqJmKB57SkKmnixCWYhoy",
      "x-amz-date": "20160425T180721Z",
      "x-amz-algorithm": "AWS4-HMAC-SHA256",
      "x-amz-signature": "bOSxtzlFNaoAfa6rzjimXBN1KIE1uQ8k1h1sCn0U7lvwYK8whuflP5PcFU8KgzxQ"
    }
  }

To upload the file to AWS S3, send the file via POST to the URL given in the
response and include all :code:`fields` with the request payload.

.. code-block::

  POST https://s3.amazonaws.com/some-bucket
  Content-Type:multipart/form-data; boundary=----WebKitFormBoundary7LwCXdHGMv2KBDza

  ------WebKitFormBoundary7LwCXdHGMv2KBDza
  Content-Disposition: form-data; name="key"

  file.txt
  ------WebKitFormBoundary7LwCXdHGMv2KBDza
  Content-Disposition: form-data; name="x-amz-algorithm"

  AWS4-HMAC-SHA256
  ------WebKitFormBoundary7LwCXdHGMv2KBDza
  Content-Disposition: form-data; name="x-amz-date"

  20160425T180721Z
  ------WebKitFormBoundary7LwCXdHGMv2KBDza
  Content-Disposition: form-data; name="x-amz-signature"

  bOSxtzlFNaoAfa6rzjimXBN1KIE1uQ8k1h1sCn0U7lvwYK8whuflP5PcFU8KgzxQ
  ------WebKitFormBoundary7LwCXdHGMv2KBDza
  Content-Disposition: form-data; name="policy"

  AORKx5gcfIIMJQUyKAkdCUDapV99I8PAn592rjN2of6Hodk1HNiFrj1ItWdJpuQiwrYVi0NJMnfCxfmfVlZg9NDpKFQi8b5vSpWpamMu5UVUdg9c8A77lF1fuWOty8Xx4qUza8EXxuz49mYYRhRym8TRNzx4v9qDwPmILe6FRl7BGSlIijn46Td9OroAHJoUPp2YU1dwsGOXGZufCGHJ8C3m1vM0YmPhDTvt2WABGscgqJmKB57SkKmnixCWYhoy
  ------WebKitFormBoundary7LwCXdHGMv2KBDza
  Content-Disposition: form-data; name="x-amz-credential"

  HKJXXOZ7L71OMC9S830I/20160425/us-east-1/s3/aws4_request
  ------WebKitFormBoundary7LwCXdHGMv2KBDza
  Content-Disposition: form-data; name="file"

  Content-Disposition: form-data; name="file"; filename="file.txt"
  Content-Type: application/octet-stream

  ------WebKitFormBoundary7LwCXdHGMv2KBDza


.. |build-status-image| image:: https://travis-ci.org/Cadasta/django-buckets.svg?branch=master
    :target: https://travis-ci.org/Cadasta/django-buckets
.. |pypi-version| image:: https://img.shields.io/pypi/v/django-buckets.svg
    :target: https://pypi.python.org/pypi/django-buckets
