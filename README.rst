django-buckets
===============================================================================

Upload files to S3 using pre-signed URLs

API
-------------------------------------------------------------------------------

If you are building an API-only application, you can get a signed URL by
POSTing `client_method` and `http_method`.

Request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block::

    POST /s3/signed-url/
    Accept: application/json
    Content-Type: application/json

    {
        "client_method": "object_get",
        "http_method": "GET"
    }

Response
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block::

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
        "signed_url": "https://s3.amazonaws.com/some-bucket/..."
    }
