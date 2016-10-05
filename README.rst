django-buckets
===============================================================================

|pypi-version| |build-status-image|

django-buckets provides a Django storage system (:code:`S3Storage`) to store files on 
`Amazon S3 <https://aws.amazon.com/s3/>`_. Besides the storage itself, the 
library comes with a custom model field (:code:`S3FileField`) to reference 
files in Django and a form widget that handles uploading files to S3 using 
`pre-signed URLs <http://docs.aws.amazon.com/AmazonS3/latest/dev/PresignedUrlUploadObject.html>`_.

For testing and development, django-buckets offers :code:`S3FakeStorage` and
the API endpoint :code:`/media/s3/uploads`, which mimics the behavior of
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

In settings, add :code:`buckets` to installed apps and set :code:`S3Storage` 
as default storage. Configure the :code:`AWS` settings by providing the S3 
bucket name AWS access key and secret key and the AWS region where your 
bucket is located.

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
    'REGION': 'us-east-1'
  }

Include django-buckets' URLs to add an `API endpoint <#api>`_, which is
used by the form widget or REST-clients to request valid signed URLs.

.. code-block:: python

  urlpatterns = [
      url(r'', include('buckets.urls')),
  ]

Edit the CORS policy of the S3 bucket you intend to use to allow for POST
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

In settings, add :code:`buckets` to installed apps and set
:code:`FakeS3Storage` as default default storage.

.. code-block:: python

 DEFAULT_FILE_STORAGE = 'buckets.test.storage.FakeS3Storage'

Include django-buckets' URLs to add an `API endpoint <#api>`_, which is
used by the form widget or REST-clients to request valid signed URLs. Further,
it will add a file upload endpoint, which behaves like S3's file upload but
stores files on the local file system, so you don't need to configure an S3 
bucket for development. 

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

Create a model with an :code:`S3FileField`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a model class, which has an :code:`S3FileField`. Internally, S3FileField
is a Django `CharField <https://docs.djangoproject.com/en/1.9/ref/models/fields/#charfield>`_
and it accepts the same arguments. 

:code:`S3FileField` accepts two additional optional arguments:

- :code:`upload_to` defines an upload directory, where uploaded files should are (similar to `FileField <https://docs.djangoproject.com/en/1.9/ref/models/fields/#filefield>`_)
- :code:`accepted_types` defines a list mime types that are accepted to upload. If you do not provide this argument, all types will be accepted. 

.. code-block:: python

  from django.db import models
  from buckets.fields import S3FileField

  class MyModel(models.Model):
      name = models.CharField(max_length=200)
      file = S3FileField(upload_to='some-dir',
                         accepted_types=['image/png', image/jpeg])


Instanciate the model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An :code:`S3FileField` accepts an URL as its value:

.. code-block:: python

  file_model = MyModel.objects.create(
      name='My File',
      file='https://s3.amazonaws.com/some-bucket/file.txt'
  )

Reading and writing the file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Internally, an instance of :code:`S3File` is created from the URL that provides
access to the file itself. 

.. code-block:: python

  # downloads the file and returns a File object
  file = file_model.file.open()

  # assign an updated file
  file_model.file = file

Usage with Django forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

django-buckets comes with a form widget that takes care of uploading files,
displaying links to files and filling the form fields. It's the easiest way to
use django-buckets in your application. 

To use the widget, make sure the widget's media files (some JS and CSS) are
added to the template, ideally somewhere in the page's :code:`head`:

.. code-block:: html

  <html>
    <head>
      <meta charset="utf-8">
      <title>django-buckets File Upload</title>
      {{ form.media }}
    </head>
    ...
  </html>

You can use Django's standard form rendering methods and the necessary HTML 
elements are added to the page:

.. code-block:: html

  <html>
    ...
    <body>
      {{ form.as_p }}
    </body>
  </html>


Use a custom widget
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you plan to use a custom widget in your forms, you can add a Django 
:code:`CharField` to your form and provide the widget you want to use:

.. code-block:: python

  from django import forms
  from .models import MyModel

  class MyModelForm(forms.ModelForm):
      file = forms.CharField(widget=MyWidget)

      class Meta:
          model = MyModel
          fields = ['name', 'file']



API
-------------------------------------------------------------------------------

Getting a signed URL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are building an API-only application, you can get a signed URL by
POSTing :code:`client_method` and :code:`http_method`.

Request
`````````````

.. code-block::

  POST /s3/signed-url/
  Accept: application/json
  Content-Type: application/json

  {
    "key": "file.txt"
  }

Response
`````````````

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


Deleting a file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Request
`````````````

.. code-block::

  POST /s3/delete-resource/
  Accept: application/json
  Content-Type: application/json

  {
    "key": "file.txt"
  }


Response
`````````````

*When the file was deleted successfully:*

.. code-block::

  HTTP/1.1 204 No Content

*When the file was not found:*

.. code-block::

  HTTP/1.1 400 Bad Request
  Content-Type: application/json

  {
    "error": "S3 resource does not exist."
  }
