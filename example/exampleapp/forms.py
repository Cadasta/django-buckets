from django import forms
from .models import FileModel


class FileForm(forms.ModelForm):
    class Meta:
        model = FileModel
        fields = ['name', 'file']
