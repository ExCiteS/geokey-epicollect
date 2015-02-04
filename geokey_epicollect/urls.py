from django.conf.urls import patterns, url

from views import (
    IndexPage, EpiCollectProject, EpiCollectUploadView, EpiCollectDownloadView
)

urlpatterns = patterns(
    '',
    url(
        r'^admin/epicollect/$',
        IndexPage.as_view(),
        name='index'),
    url(
        r'^api/epicollect/projects/(?P<project_id>[0-9]+).xml$',
        EpiCollectProject.as_view(),
        name='project_form'),
    url(
        r'^api/epicollect/projects/(?P<project_id>[0-9]+)/download/$',
        EpiCollectDownloadView.as_view(),
        name='download'),
    url(
        r'^api/epicollect/projects/(?P<project_id>[0-9]+)/upload/$',
        EpiCollectUploadView.as_view(),
        name='upload')
)
