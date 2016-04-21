from django.conf.urls import url
from . import views

urlpatterns = [
    url(
        r'^files/$',
        views.FileList.as_view(),
        name='file_list'),
    url(
        r'^files/create/$',
        views.FileCreate.as_view(),
        name='file_create'),
    url(
        r'^files/(?P<pk>[0-9]+)/$',
        views.FileUpdate.as_view(),
        name='file_update'),
]
