import json
from buckets.widgets import S3FileUploadWidget
from buckets.fields import S3File, S3FileField
from django.conf import settings  # noqa


def test_render_empty():
    expected = (
        '<div class="s3-buckets "'
        '     data-upload-to="" >'
        '   '
        '   <div class="file-links">'
        '       <a class="file-link" href=""></a>'
        '       <a class="file-remove" href="#">(Remove)</a>'
        '   </div>'
        '   <input class="file-url" type="hidden" value=""'
        '          id="None" name="{name}" />'
        '   <input class="file-input" type="file" />'
        '</div>'.format(
            name='file'
        )
    )

    widget = S3FileUploadWidget()
    actual = widget.render('file', None)

    assert actual == expected


def test_render_value():
    file = S3File('/someurl/text.txt', S3FileField())
    expected = (
        '<div class="s3-buckets uploaded"'
        '     data-upload-to="test" >'
        '   '
        '   <div class="file-links">'
        '       <a class="file-link" href="{value}">{file_name}</a>'
        '       <a class="file-remove" href="#">(Remove)</a>'
        '   </div>'
        '   <input class="file-url" type="hidden" value="{value}"'
        '          id="None" name="{name}" />'
        '   <input class="file-input" type="file" />'
        '</div>'.format(
            name='file',
            value='/someurl/text.txt',
            file_name='text.txt'
        )
    )

    widget = S3FileUploadWidget(upload_to='test')
    actual = widget.render('file', file)

    assert actual == expected


def test_render_value_from_string():
    expected = (
        '<div class="s3-buckets uploaded"'
        '     data-upload-to="test" >'
        '   '
        '   <div class="file-links">'
        '       <a class="file-link" href="{value}">{file_name}</a>'
        '       <a class="file-remove" href="#">(Remove)</a>'
        '   </div>'
        '   <input class="file-url" type="hidden" value="{value}"'
        '          id="None" name="{name}" />'
        '   <input class="file-input" type="file" />'
        '</div>'.format(
            name='file',
            value='/someurl/text.txt',
            file_name='text.txt'
        )
    )

    widget = S3FileUploadWidget(upload_to='test')
    actual = widget.render('file', '/someurl/text.txt')

    assert actual == expected


def test_render_acctepted_type():
    expected = (
        '<div class="s3-buckets "'
        '     data-upload-to="" {accepted_types}>'
        '   '
        '   <div class="file-links">'
        '       <a class="file-link" href=""></a>'
        '       <a class="file-remove" href="#">(Remove)</a>'
        '   </div>'
        '   <input class="file-url" type="hidden" value=""'
        '          id="None" name="{name}" />'
        '   <input class="file-input" type="file" />'
        '</div>'.format(
            name='file',
            accepted_types='data-accepted-types="image/gif,image/png"'
        )
    )

    widget = S3FileUploadWidget(accepted_types=['image/gif', 'image/png'])
    actual = widget.render('file', None)

    assert actual == expected


def test_render_mime_lookup(settings):  # noqa
    settings.MIME_LOOKUPS = {'key': 'value'}
    expected = (
        '<div class="s3-buckets "'
        '     data-upload-to="" {accepted_types}>'
        '   <script>var MIME_LOOKUPS = {lookups}</script>'
        '   <div class="file-links">'
        '       <a class="file-link" href=""></a>'
        '       <a class="file-remove" href="#">(Remove)</a>'
        '   </div>'
        '   <input class="file-url" type="hidden" value=""'
        '          id="None" name="{name}" />'
        '   <input class="file-input" type="file" />'
        '</div>'.format(
            name='file',
            accepted_types='data-accepted-types="image/gif,image/png"',
            lookups=json.dumps(settings.MIME_LOOKUPS)
        )
    )

    widget = S3FileUploadWidget(accepted_types=['image/gif', 'image/png'])
    actual = widget.render('file', None)

    assert actual == expected
