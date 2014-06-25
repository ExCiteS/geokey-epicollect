# from lxml import etree
from django.test import TestCase

from ..serializer import ProjectFormSerializer
from observationtypes.tests.model_factories import TextFieldFactory


class ProjectFormSerializerTest(TestCase):
    def test_serialize_textfield(self):
        text_field = TextFieldFactory()
        serializer = ProjectFormSerializer()
        xml = serializer.serialize_textfield(text_field)

        self.assertEqual(xml.attrib['ref'], text_field.key)
        self.assertEqual(xml.attrib['required'], 'false')
        self.assertEqual(xml[0].tag, 'label')
        self.assertEqual(xml[0].text, text_field.name)

    def test_serialize_required_textfield(self):
        text_field = TextFieldFactory(**{'required': True})
        serializer = ProjectFormSerializer()
        xml = serializer.serialize_textfield(text_field)

        self.assertEqual(xml.attrib['ref'], text_field.key)
        self.assertEqual(xml.attrib['required'], 'true')
        self.assertEqual(xml[0].tag, 'label')
        self.assertEqual(xml[0].text, text_field.name)

    # def test_serialize_number_field(self):
    #     pass

    # def test_serialize_truefalse_field(self):
    #     pass

    # def test_serialize_datetime_field(self):
    #     pass

    # def test_serialize_single_lookup_field(self):
    #     pass
