from django.views.generic import View
from django.http import HttpResponse

from lxml import etree

from projects.models import Project
from observationtypes.models import ObservationType
from contributions.serializers import ContributionSerializer

from serializer import ProjectFormSerializer


class EpiCollectProject(View):
    def get(self, request, project_id):
        project = Project.objects.get(pk=project_id)
        if not project.isprivate:
            serializer = ProjectFormSerializer()
            xml = serializer.serialize(project, request.get_host())
            return HttpResponse(
                etree.tostring(xml), content_type='text/xml; charset=utf-8')


class EpiCollectUploadView(View):
    def post(self, request, project_id):
        project = Project.objects.get(pk=project_id)
        if not project.isprivate:
            data = request.POST

            observation = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [
                        float(data['location_lon']),
                        float(data['location_lat'])
                    ]
                },
                'properties': {
                    'user': project.creator.id,
                    'project': project_id,
                    'observationtype': data['observationtype']
                }
            }
            observationtype = ObservationType.objects.get(
                pk=data['observationtype'])

            for field in observationtype.fields.all():
                observation['properties'][field.key] = data[field.key]

            ContributionSerializer(data=observation)
            return HttpResponse('1')
        else:
            return HttpResponse('0')


class EpiCollectDownloadView(View):
    def get(self, request, project_id):
        project = Project.objects.get(pk=project_id)
        if not project.isprivate:
            # serialize observations
            pass
