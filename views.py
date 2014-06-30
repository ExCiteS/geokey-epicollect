from django.views.generic import View
from django.http import HttpResponse

from lxml import etree

from projects.models import Project
from serializer import ProjectFormSerializer


class EpiCollectProject(View):
    def get(self, request, project_id):
        print 'get'
        project = Project.objects.get(pk=project_id)
        if not project.isprivate:
            serializer = ProjectFormSerializer()
            xml = serializer.serialize(project, request.get_host())
            return HttpResponse(
                etree.tostring(xml), content_type='text/xml; charset=utf-8')


def upload(request):
    pass


def download(request):
    pass
