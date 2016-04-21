from django.core.urlresolvers import reverse
from django.views.generic import ListView, CreateView, UpdateView

from . import forms, models


class FileViewMixin:
    model = models.FileModel
    form_class = forms.FileForm
    template_name = 'filemodel_form.html'

    def get_success_url(self):
        return reverse(
            'file_update',
            kwargs={'pk': self.object.pk}
        )


class FileList(ListView):
    model = models.FileModel
    template_name = 'filemodel_list.html'


class FileCreate(FileViewMixin, CreateView):
    pass


class FileUpdate(FileViewMixin, UpdateView):
    pass
