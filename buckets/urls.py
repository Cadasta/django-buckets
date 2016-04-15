from django.conf.urls import url
from buckets import views

urlpatterns = [
    url(r'^s3/signed-url/$', views.signed_url, name='s3_signed_url'),
]
