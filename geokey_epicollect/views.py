import json
from django.http import HttpResponse
from django.views.generic import TemplateView
from braces.views import LoginRequiredMixin

from lxml import etree
from rest_framework import status
from rest_framework.views import APIView

from geokey.projects.models import Project
from geokey.categories.models import Category
from geokey.contributions.serializers import ContributionSerializer
from geokey.contributions.models import ImageFile, MediaFile
from geokey.users.models import User

from serializer import ProjectFormSerializer, DataSerializer
from .models import (
    EpiCollectMedia,
    EpiCollectProject as EpiCollectProjectModel
)


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
        except EpiCollectProjectModel.DoesNotExist:
            return HttpResponse('0')

        user = User.objects.get(display_name='AnonymousUser')
        upload_type = request.GET.get('type')

        if upload_type == 'data':
            data = request.POST

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
                    'location_acc': data.get('location_acc'),
                    'location_provider': data.get('location_provider'),
                    'location_alt': data.get('location_alt'),
                    'location_bearing': data.get('location_bearing'),
                    'unique_id': data.get('unique_id'),
                    'DeviceID': request.GET.get('phoneid')
                },
                'meta': {
                    'category': data.get('category'),
                }
            }
            category = Category.objects.get(pk=data.get('category'))

            for field in category.fields.all():
                key = field.key.replace('-', '_')
                value = data.get(key + '_' + str(category.id))
                if field.fieldtype == 'MultipleLookupField':
                    value = json.loads('[' + value + ']')

                observation['properties'][field.key] = value

            contribution = ContributionSerializer(
                data=observation,
                context={'user': user, 'project': epicollect.project}
            )
            if contribution.is_valid(raise_exception=True):
                contribution.save()

            photo_id = data.get('photo')
            if photo_id is not None:
                EpiCollectMedia.objects.create(
                    contribution=contribution.instance,
                    file_name=photo_id
                )

            video_id = data.get('video')
            if video_id is not None:
                EpiCollectMedia.objects.create(
                    contribution=contribution.instance,
                    file_name=video_id
                )

            return HttpResponse('1')

        elif upload_type == 'thumbnail':
            for key in request.FILES:
                epicollect_file = EpiCollectMedia.objects.get(
                    file_name=key[:key.rfind('.')]
                )
                file = request.FILES.get(key)

                ImageFile.objects.create(
                    name=key,
                    description='',
                    creator=user,
                    contribution=epicollect_file.contribution,
                    image=file
                )

                epicollect_file.delete()

            return HttpResponse('1')

        elif upload_type == 'video':
            file = request.FILES.get('name')
            name = file._name
            epicollect_file = EpiCollectMedia.objects.get(file_name=name)

            MediaFile.objects._create_video_file(
                name, '', user, epicollect_file.contribution, file)
            epicollect_file.delete()
            return HttpResponse('1')


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
