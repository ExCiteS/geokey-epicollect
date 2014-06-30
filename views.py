from lxml import etree
from django.views.generic.base import View
from django.http import HttpResponse

from projects.models import Project

from serializer import ProjectFormSerializer


class EpiCollectProject(View):
    def get(self, request, project_id):
        project = Project.objects.get(pk=project_id)
        if not project.isprivate:
            serializer = ProjectFormSerializer()
            xml = serializer.serialize(project, request.get_host())
            return HttpResponse(etree.tostring(xml), content_type="application/xml")


def upload(request):
    pass


def download(request):
    pass
