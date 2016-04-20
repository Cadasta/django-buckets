from buckets.widgets import S3FileUploadWidget
from buckets.test.storage import FakeS3Storage


def test_render_empty():
    storage = FakeS3Storage()
    expected = (
        '<div class="s3-buckets " data-upload-url="{upload_url}">'
        '   <div class="file-links">'
        '       <a class="file-link" href=""></a>'
        '       <a class="file-remove" href="#">(Remove)</a>'
        '   </div>'
        '   <input class="file-url" type="hidden" value=""'
        '          id="None" name="{name}" />'
        '   <input class="file-input" type="file" />'
        '</div>'.format(
            upload_url=storage.get_signed_url(client_method='put_object',
                                              http_method='PUT'),
            name='file'
        )
    )

    widget = S3FileUploadWidget(storage=storage)
    actual = widget.render('file', None)

    assert actual == expected


def test_render_value():
    storage = FakeS3Storage()
    expected = (
        '<div class="s3-buckets uploaded" data-upload-url="{upload_url}">'
        '   <div class="file-links">'
        '       <a class="file-link" href="{value}">{file_name}</a>'
        '       <a class="file-remove" href="#">(Remove)</a>'
        '   </div>'
        '   <input class="file-url" type="hidden" value="{value}"'
        '          id="None" name="{name}" />'
        '   <input class="file-input" type="file" />'
        '</div>'.format(
            upload_url=storage.get_signed_url(client_method='put_object',
                                              http_method='PUT'),
            name='file',
            value='/someurl/text.txt',
            file_name='text.txt'
        )
    )

    widget = S3FileUploadWidget(storage=storage)
    actual = widget.render('file', '/someurl/text.txt')

    assert actual == expected
