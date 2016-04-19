from django.views.generic import CreateView, UpdateView

from . import forms, models


class FileCreateView(CreateView):
    model = models.FileModel
    form_class = forms.FileForm
    template_name = 'filemodel_form.html'


class FileUpdateView(UpdateView):
    model = models.FileModel
