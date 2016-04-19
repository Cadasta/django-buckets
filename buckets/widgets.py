from os.path import basename
from django.forms import widgets
from django.utils.safestring import mark_safe


class S3FileUploadWidget(widgets.TextInput):
    default_html = (
        '<div class="s3upload">'
        '   <input class="file-url" type="hidden" value="{file_url}" id="{element_id}" name="{name}" />'
        '   <input class="file-destination" type="hidden" value="{dest}">'
        '   <input class="file-input" type="file" />'
        '</div>'
    )

    def __init__(self, *args, **kwargs):
        self.html = kwargs.pop('html', self.default_html)
        storage = kwargs.pop('storage')
        self.dest = storage.get_signed_url(client_method='put_object',
                                           http_method='PUT')
        print('self.dest')
        super(S3FileUploadWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        output = self.html.format(
            name=name,
            file_url=value or '',
            element_id=self.build_attrs(attrs).get('id'),
            file_name=basename(value or ''),
            dest=self.dest,
        )

        return mark_safe(output)
