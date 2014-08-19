from django.http import HttpResponse

from lxml import etree
from rest_framework.views import APIView

from projects.models import Project
from observationtypes.models import ObservationType
from contributions.serializers import ContributionSerializer

from serializer import ProjectFormSerializer, DataSerializer
from users.models import User


class EpiCollectProject(APIView):
    def get(self, request, project_id):
        project = Project.objects.get(pk=project_id)
        if not project.isprivate:
            serializer = ProjectFormSerializer()
            xml = serializer.serialize(project, request.get_host())
            return HttpResponse(
                etree.tostring(xml), content_type='text/xml; charset=utf-8')


class EpiCollectUploadView(APIView):
    def post(self, request, project_id):
        project = Project.objects.get(pk=project_id)

        if not project.isprivate and project.everyone_contributes:
            data = request.POST
            user = User.objects.get(display_name='AnonymousUser')
            project = Project.objects.get(pk=project_id)

            observation = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [
                        float(data.get('location_lon')),
                        float(data.get('location_lat'))
                    ]
                },
                'properties': {
                    'contributiontype': data.get('contributiontype')
                }
            }
            observationtype = ObservationType.objects.get(
                pk=data.get('contributiontype'))

            for field in observationtype.fields.all():
                observation['properties'][field.key] = data.get(field.key + '_' + str(observationtype.id))

            ContributionSerializer(
                data=observation,
                context={'user': user, 'project': project}
            )
            return HttpResponse('1')

        return HttpResponse('0')


class EpiCollectDownloadView(APIView):
    def get(self, request, project_id):
        project = Project.objects.get(pk=project_id)
        if not project.isprivate:
            serializer = DataSerializer()
            xml = serializer.serialize(project)
            return HttpResponse(
                etree.tostring(xml), content_type='text/xml; charset=utf-8')
