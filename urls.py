from django.conf.urls import patterns, url

from views import upload, download

urlpatterns = patterns(
    '',
    url(
        r'^projects/(?P<project_id>[0-9]+)/download/$',
        download,
        name='download'),
    url(
        r'^projects/(?P<project_id>[0-9]+)/upload/$',
        upload,
        name='upload')
)
