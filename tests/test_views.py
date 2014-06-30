from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase, APIRequestFactory

from projects.tests.model_factories import ProjectF
from observationtypes.tests.model_factories import (
    ObservationTypeFactory, TextFieldFactory
)

from ..views import EpiCollectProject


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
