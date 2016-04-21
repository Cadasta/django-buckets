from os.path import basename
from django.forms import widgets
from django.utils.safestring import mark_safe


class S3FileUploadWidget(widgets.TextInput):
    default_html = (
        '<div class="s3-buckets {uploaded_class}"'
        '     data-upload-url="{upload_url}">'
        '   <div class="file-links">'
        '       <a class="file-link" href="{file_url}">{file_name}</a>'
        '       <a class="file-remove" href="#">(Remove)</a>'
        '   </div>'
        '   <input class="file-url" type="hidden" value="{file_url}"'
        '          id="{element_id}" name="{name}" />'
        '   <input class="file-input" type="file" />'
        '</div>'
    )

    class Media:
        js = (
            'buckets/js/script.js',
        )
        css = {
            'all': (
                'buckets/css/buckets.css',
            )
        }

    def __init__(self, *args, **kwargs):
        self.html = kwargs.pop('html', self.default_html)
        storage = kwargs.pop('storage')
        self.upload_url = storage.get_signed_url(client_method='put_object',
                                                 http_method='PUT')

        super(S3FileUploadWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        file_url = value.url if value else ''

        output = self.html.format(
            name=name,
            file_url=file_url,
            element_id=self.build_attrs(attrs).get('id'),
            file_name=basename(file_url) if file_url else '',
            upload_url=self.upload_url,
            uploaded_class=('uploaded' if value else '')
        )

        return mark_safe(output)
