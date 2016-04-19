from django.conf.urls import include, url
from buckets.test import views

urlpatterns = [
    url(r'^', include('buckets.urls')),
    url(r'^s3/files/$', views.fake_s3_upload, name='fake_s3_upload'),
]
