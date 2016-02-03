from django.test import TestCase
from django.core.urlresolvers import reverse
from django.http import HttpRequest, QueryDict
from django.contrib.auth.models import AnonymousUser
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site

from rest_framework.test import APITestCase, APIRequestFactory

from geokey import version
from geokey.core.tests.helpers import render_helpers
from geokey.users.models import User
from geokey.users.tests.model_factories import UserFactory
from geokey.projects.models import Project
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.contributions.tests.model_factories import ObservationFactory
from geokey.contributions.tests.media.model_factories import get_image
from geokey.categories.tests.model_factories import (
    CategoryFactory, TextFieldFactory, MultipleLookupFieldFactory,
    MultipleLookupValueFactory
)
from ..models import (
    EpiCollectMedia, EpiCollectProject as EpiCollectProjectModel
)
from ..views import (
    IndexPage, EpiCollectProject, EpiCollectUploadView, EpiCollectDownloadView
)


class IndexPageTest(TestCase):
    def setUp(self):
        self.view = IndexPage.as_view()
        self.request = HttpRequest()
        self.request.method = 'GET'
        self.request.user = AnonymousUser()
        self.request.META['SERVER_NAME'] = 'localhost'
        self.request.META['SERVER_PORT'] = '8000'

    def test_get_with_anonymous(self):
        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_get_with_user(self):
        project = ProjectFactory.create(**{'isprivate': False})
        enabled = EpiCollectProjectModel.objects.create(
            project=project, enabled=True
        )

        self.request.user = project.creator
        response = self.view(self.request).render()

        rendered = render_to_string(
            'epicollect_index.html',
            {
                'projects': [project],
                'epicollect': [enabled],
                'host': self.request.get_host(),
                'user': project.creator,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version
            }
        )
        self.assertEqual(response.status_code, 200)
        response = render_helpers.remove_csrf(response.content.decode('utf-8'))
        self.assertEqual(response, rendered)

    def test_post_with_anonymous(self):
        project = ProjectFactory.create(**{'isprivate': False})
        EpiCollectProjectModel.objects.create(
            project=project, enabled=True
        )
        self.request.method = 'POST'
        self.request.POST = {
            'epicollect_project': []
        }
        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])
        self.assertEqual(EpiCollectProjectModel.objects.count(), 1)

    def test_post_with_user(self):
        user = UserFactory.create()
        project = ProjectFactory.create(
            **{'isprivate': False, 'creator': user})
        to_enable = ProjectFactory.create(
            **{'isprivate': False, 'creator': user})
        EpiCollectProjectModel.objects.create(
            project=project, enabled=True
        )
        self.request.method = 'POST'
        self.request.POST = QueryDict('epicollect_project=%s' % to_enable.id)
        self.request.user = user
        response = self.view(self.request).render()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(EpiCollectProjectModel.objects.count(), 1)
        rendered = render_to_string(
            'epicollect_index.html',
            {
                'projects': [
                    Project.objects.get(pk=project.id),
                    Project.objects.get(pk=to_enable.id)
                ],
                'epicollect': [],
                'host': self.request.get_host(),
                'user': project.creator,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version
            }
        )
        response = render_helpers.remove_csrf(response.content.decode('utf-8'))
        self.assertEqual(response, rendered)


class ProjectDescriptionViewTest(APITestCase):
    def test_get_project(self):
        project = ProjectFactory.create(**{'isprivate': False})
        EpiCollectProjectModel.objects.create(project=project, enabled=True)
        type1 = CategoryFactory.create(**{'project': project})
        TextFieldFactory(**{'category': type1})
        type2 = CategoryFactory.create(**{'project': project})
        TextFieldFactory(**{'category': type2})
        type3 = CategoryFactory.create(**{'project': project})
        TextFieldFactory(**{'category': type3})
        factory = APIRequestFactory()
        request = factory.get(
            reverse('geokey_epicollect:project_form', args=(project.id, )))

        view = EpiCollectProject.as_view()
        response = view(request, project_id=project.id)
        self.assertEqual(response.status_code, 200)

    def test_get_not_existing_project(self):
        factory = APIRequestFactory()
        request = factory.get(
            reverse('geokey_epicollect:project_form', args=(45454544, )))

        view = EpiCollectProject.as_view()
        response = view(request, project_id=45454544)
        self.assertEqual(response.status_code, 403)
        self.assertIn(
            response.content,
            '<error>The project must enabled for EpiCollect.</error>'
        )


class UploadDataTest(APITestCase):
    def setUp(self):
        if not User.objects.filter(display_name='AnonymousUser').exists():
            UserFactory.create(display_name='AnonymousUser')

    def test_upload_data(self):
        project = ProjectFactory.create(
            **{'isprivate': False, 'everyone_contributes': True}
        )
        EpiCollectProjectModel.objects.create(project=project, enabled=True)
        type1 = CategoryFactory.create(**{'project': project})
        field = TextFieldFactory(**{'category': type1})

        data = ('location_lat=51.5175205&location_lon=-0.1729205&location_acc='
                '20&location_alt=&location_bearing=&category={category}&'
                '{field_key}_{category}=Westbourne+Park'.format(
                    category=type1.id,
                    field_key=field.key)
                )

        factory = APIRequestFactory()
        url = reverse('geokey_epicollect:upload', kwargs={
            'project_id': project.id
        })
        request = factory.post(
            url + '?type=data',
            data,
            content_type='application/x-www-form-urlencoded'
        )

        view = EpiCollectUploadView.as_view()
        response = view(request, project_id=project.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '1')

    def test_upload_data_with_media(self):
        project = ProjectFactory.create(
            **{'isprivate': False, 'everyone_contributes': True}
        )
        EpiCollectProjectModel.objects.create(project=project, enabled=True)
        type1 = CategoryFactory.create(**{'project': project})
        field = TextFieldFactory(**{'category': type1})

        data = ('location_lat=51.5175205&location_lon=-0.1729205&location_acc='
                '20&location_alt=&location_bearing=&category={category}&'
                '{field_key}_{category}=Westbourne+Park&photo=abc&'
                'video=def'.format(
                    category=type1.id,
                    field_key=field.key)
                )

        factory = APIRequestFactory()
        url = reverse('geokey_epicollect:upload', kwargs={
            'project_id': project.id
        })
        request = factory.post(
            url + '?type=data',
            data,
            content_type='application/x-www-form-urlencoded'
        )

        view = EpiCollectUploadView.as_view()
        response = view(request, project_id=project.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EpiCollectMedia.objects.count(), 2)
        self.assertEqual(response.content, '1')

    def test_upload_data_without_location(self):
        project = ProjectFactory.create(
            **{'isprivate': False, 'everyone_contributes': True}
        )
        EpiCollectProjectModel.objects.create(project=project, enabled=True)
        type1 = CategoryFactory.create(**{'project': project})
        field = TextFieldFactory(**{'category': type1})

        data = ('category={category}&{field_key}_{category}=Westbourne+'
                'Park'.format(
                    category=type1.id,
                    field_key=field.key)
                )

        factory = APIRequestFactory()
        url = reverse('geokey_epicollect:upload', kwargs={
            'project_id': project.id
        })
        request = factory.post(
            url + '?type=data',
            data,
            content_type='application/x-www-form-urlencoded'
        )

        view = EpiCollectUploadView.as_view()
        response = view(request, project_id=project.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '0')

    def test_upload_category_does_not_exist(self):
        project = ProjectFactory.create(
            **{'isprivate': False, 'everyone_contributes': True}
        )
        EpiCollectProjectModel.objects.create(project=project, enabled=True)

        data = ('location_lat=51.5175205&location_lon=-0.1729205&location_acc='
                '20&location_alt=&location_bearing=&category=218421894')

        factory = APIRequestFactory()
        url = reverse('geokey_epicollect:upload', kwargs={
            'project_id': project.id
        })
        request = factory.post(
            url + '?type=data',
            data,
            content_type='application/x-www-form-urlencoded'
        )

        view = EpiCollectUploadView.as_view()
        response = view(request, project_id=project.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '0')

    def test_upload_category_is_null(self):
        project = ProjectFactory.create(
            **{'isprivate': False, 'everyone_contributes': True}
        )
        EpiCollectProjectModel.objects.create(project=project, enabled=True)

        data = ('location_lat=51.5175205&location_lon=-0.1729205&location_acc='
                '20&location_alt=&location_bearing=&category=Null')

        factory = APIRequestFactory()
        url = reverse('geokey_epicollect:upload', kwargs={
            'project_id': project.id
        })
        request = factory.post(
            url + '?type=data',
            data,
            content_type='application/x-www-form-urlencoded'
        )

        view = EpiCollectUploadView.as_view()
        response = view(request, project_id=project.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '0')

    def test_upload_checkboxes(self):
        project = ProjectFactory.create(
            **{'isprivate': False, 'everyone_contributes': True}
        )
        EpiCollectProjectModel.objects.create(project=project, enabled=True)
        type1 = CategoryFactory.create(**{'project': project})
        field = MultipleLookupFieldFactory(**{'category': type1})
        val_1 = MultipleLookupValueFactory(**{'field': field})
        val_2 = MultipleLookupValueFactory(**{'field': field})

        data = ('location_lat=51.5175205&location_lon=-0.1729205&location_acc='
                '20&location_alt=&location_bearing=&category={category}&'
                '{field_key}_{category}={checkbox_1}%2c+{checkbox_2}'.format(
                    category=type1.id,
                    field_key=field.key,
                    checkbox_1=val_1.id,
                    checkbox_2=val_2.id
                ))

        factory = APIRequestFactory()
        url = reverse('geokey_epicollect:upload', kwargs={
            'project_id': project.id
        })
        request = factory.post(
            url + '?type=data',
            data,
            content_type='application/x-www-form-urlencoded'
        )

        view = EpiCollectUploadView.as_view()
        response = view(request, project_id=project.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '1')

    def test_upload_data_to_private_project(self):
        project = ProjectFactory.create()
        type1 = CategoryFactory.create(**{'project': project})
        field = TextFieldFactory(**{'category': type1})

        data = ('location_lat=51.5175205&location_lon=-0.1729205&location_acc='
                '20&location_alt=&location_bearing=&category={category}&'
                '{field_key}_{category}=Westbourne+Park'.format(
                    category=type1.id,
                    field_key=field.key)
                )

        factory = APIRequestFactory()
        url = reverse('geokey_epicollect:upload', kwargs={
            'project_id': project.id
        })
        request = factory.post(
            url + '?type=data',
            data,
            content_type='application/x-www-form-urlencoded'
        )

        view = EpiCollectUploadView.as_view()
        response = view(request, project_id=project.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '0')

    def test_upload_image(self):
        image = get_image()
        project = ProjectFactory.create()
        EpiCollectProjectModel.objects.create(project=project, enabled=True)
        contribution = ObservationFactory.create(**{'project': project})
        EpiCollectMedia.objects.create(
            contribution=contribution,
            file_name=image.name
        )

        data = {'name': image}
        factory = APIRequestFactory()
        url = reverse('geokey_epicollect:upload', kwargs={
            'project_id': project.id
        })
        request = factory.post(url + '?type=thumbnail', data)

        view = EpiCollectUploadView.as_view()
        response = view(request, project_id=project.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '1')

    def test_upload_image_with_fullimage_flag(self):
        image = get_image()
        project = ProjectFactory.create()
        EpiCollectProjectModel.objects.create(project=project, enabled=True)
        contribution = ObservationFactory.create(**{'project': project})
        EpiCollectMedia.objects.create(
            contribution=contribution,
            file_name=image.name
        )

        data = {'name': image}
        factory = APIRequestFactory()
        url = reverse('geokey_epicollect:upload', kwargs={
            'project_id': project.id
        })
        request = factory.post(url + '?type=full_image', data)

        view = EpiCollectUploadView.as_view()
        response = view(request, project_id=project.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '1')

    def test_upload_image_with_wrong_file_name(self):
        image = get_image()
        project = ProjectFactory.create()
        EpiCollectProjectModel.objects.create(project=project, enabled=True)
        contribution = ObservationFactory.create(**{'project': project})
        EpiCollectMedia.objects.create(
            contribution=contribution,
            file_name='file_name.jpg'
        )

        data = {'name': image}
        factory = APIRequestFactory()
        url = reverse('geokey_epicollect:upload', kwargs={
            'project_id': project.id
        })
        request = factory.post(url + '?type=thumbnail', data)

        view = EpiCollectUploadView.as_view()
        response = view(request, project_id=project.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '0')


class DownloadDataTest(APITestCase):
    def test_download_data(self):
        project = ProjectFactory.create(**{'isprivate': False})
        EpiCollectProjectModel.objects.create(project=project, enabled=True)
        ObservationFactory.create_batch(
            20, **{'project': project, 'properties': {'key': 'value'}})

        factory = APIRequestFactory()
        url = reverse('geokey_epicollect:download', kwargs={
            'project_id': project.id
        })
        request = factory.get(url)
        view = EpiCollectDownloadView.as_view()
        response = view(request, project_id=project.id)
        self.assertEqual(response.status_code, 200)

    def test_download_data_as_tsv(self):
        project = ProjectFactory.create(**{'isprivate': False})
        EpiCollectProjectModel.objects.create(project=project, enabled=True)
        ObservationFactory.create_batch(
            20, **{'project': project, 'properties': {'key': 'value'}})

        factory = APIRequestFactory()
        url = reverse('geokey_epicollect:download', kwargs={
            'project_id': project.id
        }) + '?xml=false'
        request = factory.get(url)
        view = EpiCollectDownloadView.as_view()
        response = view(request, project_id=project.id)
        self.assertEqual(response.status_code, 200)

    def test_download_data_non_existing_project(self):
        factory = APIRequestFactory()
        url = reverse('geokey_epicollect:download', kwargs={
            'project_id': 56456123156
        })
        request = factory.get(url)
        view = EpiCollectDownloadView.as_view()
        response = view(request, project_id=56456123156)
        self.assertEqual(response.status_code, 403)
