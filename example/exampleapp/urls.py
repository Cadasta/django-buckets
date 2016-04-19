from django.conf.urls import url
from . import views

urlpatterns = [
    url(
        r'^file/create/$',
        views.FileCreateView.as_view(),
        name='file_create'),
    url(
        r'^file/(?P<pk>[0-9]+)/$',
        views.FileCreateView.as_view(),
        name='file_update'),
]
