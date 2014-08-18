from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase, APIRequestFactory

from projects.tests.model_factories import ProjectF
from contributions.tests.model_factories import ObservationFactory
from observationtypes.tests.model_factories import (
    ObservationTypeFactory, TextFieldFactory
)

from ..views import (
    EpiCollectProject, EpiCollectUploadView, EpiCollectDownloadView
)


class ProjectDescriptionViewTest(APITestCase):
    def test_project_form(self):
        project = ProjectF.create(**{'isprivate': False})
        type1 = ObservationTypeFactory.create(**{'project': project})
        TextFieldFactory(**{'observationtype': type1})
        type2 = ObservationTypeFactory.create(**{'project': project})
        TextFieldFactory(**{'observationtype': type2})
        type3 = ObservationTypeFactory.create(**{'project': project})
        TextFieldFactory(**{'observationtype': type3})
        factory = APIRequestFactory()
        request = factory.get(
            reverse('epicollect:project_form', args=(project.id, )))

        view = EpiCollectProject.as_view()
        response = view(request, project_id=project.id)
        self.assertEqual(response.status_code, 200)


class UploadDataTest(APITestCase):
    def test_upload_data(self):
        project = ProjectF.create(
            **{'isprivate': False, 'everyone_contributes': True}
        )
        type1 = ObservationTypeFactory.create(**{'project': project})
        field = TextFieldFactory(**{'observationtype': type1})

        data = 'location_lat=51.5175205&location_lon=-0.1729205&location_acc=20&location_alt=&location_bearing=&contributiontype=' + str(type1.id) + '&' + str(field.observationtype.id) + '_' + field.key + '=Westbourne+Park'
        data = 'epicollect_insert=form1&table=EpiCollect&ecTimeCreated=1408374444168&ecPhoneID=6d8a5c6d6d97fd3f&ecJumped=27_number_of_bikes%2C27_id%2C27_street&location_lat=51.524817338213325&location_alt=109.5&location_acc=30.0&26_name=Warren+St&26_age=&form_21=071b85d2-4c91-4b8b-a0b5-566a7563ca9b&location_lon=-0.13451437465846539&27_number_of_bikes=&location_provider=gps&27_id=&location_bearing=226.0&27_street=&contributiontype=' + str(type1.id) + '&26_lines=20'

        factory = APIRequestFactory()
        url = reverse('epicollect:upload', kwargs={
            'project_id': project.id
        })
        request = factory.post(
            url, data, content_type='application/x-www-form-urlencoded')

        view = EpiCollectUploadView.as_view()
        response = view(request, project_id=project.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '1')

    def test_upload_data_to_private_project(self):
        project = ProjectF.create()
        type1 = ObservationTypeFactory.create(**{'project': project})
        field = TextFieldFactory(**{'observationtype': type1})

        data = 'location_lat=51.5175205&location_lon=-0.1729205&location_acc=20&location_alt=&location_bearing=&contributiontype=' + str(type1.id) + '&' + str(field.observationtype.id) + '_' + field.key + '=Westbourne+Park'

        factory = APIRequestFactory()
        url = reverse('epicollect:upload', kwargs={
            'project_id': project.id
        })
        request = factory.post(
            url, data, content_type='application/x-www-form-urlencoded')

        view = EpiCollectUploadView.as_view()
        response = view(request, project_id=project.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '0')


class DownloadDataTest(APITestCase):
    def test_download_data(self):
        project = ProjectF.create(**{'isprivate': False})
        ObservationFactory.create_batch(
            20, **{'project': project, 'attributes': {'key': 'value'}})

        factory = APIRequestFactory()
        url = reverse('epicollect:download', kwargs={
            'project_id': project.id
        })
        request = factory.get(url)
        view = EpiCollectDownloadView.as_view()
        response = view(request, project_id=project.id)
        self.assertEqual(response.status_code, 200)
