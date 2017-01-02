import json
from os.path import basename
from django.forms import widgets
from django.utils.safestring import mark_safe
from django.conf import settings


class S3FileUploadWidget(widgets.TextInput):
    default_html = (
        '<div class="s3-buckets {uploaded_class}"'
        '     data-upload-to="{upload_to}" {accepted_types}>'
        '   {mime_lookup}'
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

    def __init__(self, upload_to='', accepted_types=None, *args, **kwargs):
        self.html = kwargs.pop('html', self.default_html)
        self.upload_to = upload_to
        self.accepted_types = accepted_types

        super(S3FileUploadWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        if isinstance(value, str):
            file_url = value
        else:
            file_url = value.url if value else ''

        accepted_types = ''
        if self.accepted_types:
            accepted_types = 'data-accepted-types="{}"'.format(
                ','.join(self.accepted_types)
            )

        mime_lookup = ''
        if hasattr(settings, 'MIME_LOOKUPS'):
            mime_lookup = ('<script>var MIME_LOOKUPS = ' +
                           json.dumps(settings.MIME_LOOKUPS) + '</script>')

        output = self.html.format(
            name=name,
            file_url=file_url,
            element_id=self.build_attrs(attrs).get('id'),
            file_name=basename(file_url) if file_url else '',
            uploaded_class=('uploaded' if file_url else ''),
            upload_to=self.upload_to,
            accepted_types=accepted_types,
            mime_lookup=mime_lookup
        )

        return mark_safe(output)
