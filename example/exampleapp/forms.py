from django import forms
from buckets.widgets import S3FileUploadWidget
from .models import FileModel

TYPES = ['image/jpeg']


class FileForm(forms.ModelForm):
    file = forms.CharField(widget=S3FileUploadWidget(accepted_types=TYPES))

    class Meta:
        model = FileModel
        fields = ['name', 'file']
