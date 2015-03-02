import json
from django.http import HttpResponse
from django.views.generic import TemplateView
from braces.views import LoginRequiredMixin

from lxml import etree
from rest_framework import status
from rest_framework.views import APIView

from projects.models import Project
from categories.models import Category
from contributions.serializers import ContributionSerializer

from serializer import ProjectFormSerializer, DataSerializer
from users.models import User
from .models import EpiCollectProject as EpiCollectProjectModel


class IndexPage(LoginRequiredMixin, TemplateView):
    template_name = 'epicollect_index.html'
    exception_message = 'Managing Community Maps is for super-users only.'

    def get_context_data(self, *args, **kwargs):
        projects = Project.objects.filter(admins=self.request.user)
        enabled = EpiCollectProjectModel.objects.filter(project__in=projects)

        return super(IndexPage, self).get_context_data(
            projects=projects,
            epicollect=enabled,
            host=self.request.get_host(),
            *args,
            **kwargs
        )

    def update_projects(self, projects, enabled, form=[]):
        for p in projects:
            if p in enabled and not str(p.id) in form:
                EpiCollectProjectModel.objects.get(project=p).delete()
            elif p not in enabled and str(p.id) in form:
                EpiCollectProjectModel.objects.create(project=p, enabled=True)

    def post(self, request):
        context = self.get_context_data()
        self.update_projects(
            context.get('projects'),
            [epi.project for epi in context.get('epicollect')],
            self.request.POST.getlist('epicollect_project')
        )
        return self.render_to_response(context)


class EpiCollectProject(APIView):
    def get(self, request, project_id):
        try:
            epicollect = EpiCollectProjectModel.objects.get(pk=project_id)

            serializer = ProjectFormSerializer()
            xml = serializer.serialize(epicollect.project, request.get_host())
            return HttpResponse(
                etree.tostring(xml), content_type='text/xml; charset=utf-8')

        except EpiCollectProjectModel.DoesNotExist:
            return HttpResponse(
                '<error>The project must enabled for EpiCollect.</error>',
                content_type='text/xml; charset=utf-8',
                status=status.HTTP_403_FORBIDDEN
            )


class EpiCollectUploadView(APIView):
    def post(self, request, project_id):
        try:
            epicollect = EpiCollectProjectModel.objects.get(pk=project_id)
            data = request.POST
            user = User.objects.get(display_name='AnonymousUser')

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
                    'category': data.get('category'),
                    'attributes': {
                        'location_acc': data.get('location_acc'),
                        'location_provider': data.get('location_provider'),
                        'location_alt': data.get('location_alt'),
                        'location_bearing': data.get('location_bearing'),
                        'category': data.get('category'),
                        'unique_id': data.get('unique_id'),
                        'DeviceID': request.GET.get('phoneid')
                    }
                }
            }
            observationtype = Category.objects.get(
                pk=data.get('category'))

            for field in observationtype.fields.all():
                key = field.key.replace('-', '_')
                value = data.get(key + '_' + str(observationtype.id))
                if field.fieldtype == 'MultipleLookupField':
                    value = json.loads('[' + value + ']')

                observation['properties']['attributes'][field.key] = value

            ContributionSerializer(
                data=observation,
                context={'user': user, 'project': epicollect.project}
            )
            return HttpResponse('1')

        except EpiCollectProjectModel.DoesNotExist:
            return HttpResponse('0')


class EpiCollectDownloadView(APIView):
    def get(self, request, project_id):
        try:
            epicollect = EpiCollectProjectModel.objects.get(pk=project_id)

            serializer = DataSerializer()
            if request.GET.get('xml') == 'false':
                tsv = serializer.serialize_to_tsv(epicollect.project)
                return HttpResponse(
                    tsv,
                    content_type='text/plain; charset=utf-8'
                )
            else:
                xml = serializer.serialize_to_xml(epicollect.project)
                return HttpResponse(
                    etree.tostring(xml),
                    content_type='text/xml; charset=utf-8'
                )
        except EpiCollectProjectModel.DoesNotExist:
            return HttpResponse(
                '<error>The project must enabled for EpiCollect.</error>',
                content_type='text/xml; charset=utf-8',
                status=status.HTTP_403_FORBIDDEN
            )
