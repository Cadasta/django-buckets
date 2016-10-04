from django.conf.urls import url
from buckets import views

urlpatterns = [
    url(r'^s3/signed-url/$', views.signed_url, name='s3_signed_url'),
    url(r'^s3/delete-resource/$',
        views.delete_resource, name='s3_delete_resource'),
]
