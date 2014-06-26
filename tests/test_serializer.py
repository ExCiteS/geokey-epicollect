from lxml import etree
from django.test import TestCase

from ..serializer import ProjectFormSerializer
from observationtypes.tests.model_factories import (
    TextFieldFactory, NumericFieldFactory, TrueFalseFieldFactory
)


class ProjectFormSerializerTest(TestCase):
    def test_serialize_textfield(self):
        field = TextFieldFactory()
        serializer = ProjectFormSerializer()
        xml = serializer.serialize_textfield(field)

        self.assertEqual(xml.tag, 'input')
        self.assertEqual(xml.attrib['ref'], field.key)
        self.assertEqual(xml.attrib['required'], 'false')
        self.assertEqual(xml[0].tag, 'label')
        self.assertEqual(xml[0].text, field.name)

        with self.assertRaises(KeyError):
            xml.attrib['decimal']

    def test_serialize_required_textfield(self):
        field = TextFieldFactory(**{'required': True})
        serializer = ProjectFormSerializer()
        xml = serializer.serialize_textfield(field)

        self.assertEqual(xml.tag, 'input')
        self.assertEqual(xml.attrib['ref'], field.key)
        self.assertEqual(xml.attrib['required'], 'true')
        self.assertEqual(xml[0].tag, 'label')
        self.assertEqual(xml[0].text, field.name)

        with self.assertRaises(KeyError):
            xml.attrib['decimal']

    def test_serialize_number_field(self):
        field = NumericFieldFactory()
        serializer = ProjectFormSerializer()
        xml = serializer.serialize_numericfield(field)

        self.assertEqual(xml.tag, 'input')
        self.assertEqual(xml.attrib['ref'], field.key)
        self.assertEqual(xml.attrib['required'], 'false')
        self.assertEqual(xml.attrib['decimal'], 'true')
        self.assertEqual(xml[0].tag, 'label')
        self.assertEqual(xml[0].text, field.name)

    def test_serialize_required_number_field(self):
        field = NumericFieldFactory(**{'required': True})
        serializer = ProjectFormSerializer()
        xml = serializer.serialize_numericfield(field)

        self.assertEqual(xml.tag, 'input')
        self.assertEqual(xml.attrib['ref'], field.key)
        self.assertEqual(xml.attrib['required'], 'true')
        self.assertEqual(xml.attrib['decimal'], 'true')
        self.assertEqual(xml[0].tag, 'label')
        self.assertEqual(xml[0].text, field.name)

        with self.assertRaises(KeyError):
            xml.attrib['min']
            xml.attrib['max']

    def test_serialize_number_field_with_minfield(self):
        field = NumericFieldFactory(**{'required': True, 'minval': 12})
        serializer = ProjectFormSerializer()
        xml = serializer.serialize_numericfield(field)

        self.assertEqual(xml.tag, 'input')
        self.assertEqual(xml.attrib['ref'], field.key)
        self.assertEqual(xml.attrib['required'], 'true')
        self.assertEqual(xml.attrib['decimal'], 'true')
        self.assertEqual(xml.attrib['min'], '12')

        with self.assertRaises(KeyError):
            xml.attrib['max']

        self.assertEqual(xml[0].tag, 'label')
        self.assertEqual(xml[0].text, field.name)

    def test_serialize_number_field_with_maxfield(self):
        field = NumericFieldFactory(**{'required': True, 'maxval': 12})
        serializer = ProjectFormSerializer()
        xml = serializer.serialize_numericfield(field)

        self.assertEqual(xml.tag, 'input')
        self.assertEqual(xml.attrib['ref'], field.key)
        self.assertEqual(xml.attrib['required'], 'true')
        self.assertEqual(xml.attrib['decimal'], 'true')
        self.assertEqual(xml.attrib['max'], '12')
        with self.assertRaises(KeyError):
            xml.attrib['min']
        self.assertEqual(xml[0].tag, 'label')
        self.assertEqual(xml[0].text, field.name)

    def test_serialize_number_field_with_minmaxfield(self):
        field = NumericFieldFactory(
            **{'required': True, 'minval': 2, 'maxval': 12})
        serializer = ProjectFormSerializer()
        xml = serializer.serialize_numericfield(field)

        self.assertEqual(xml.tag, 'input')
        self.assertEqual(xml.attrib['ref'], field.key)
        self.assertEqual(xml.attrib['required'], 'true')
        self.assertEqual(xml.attrib['decimal'], 'true')
        self.assertEqual(xml.attrib['min'], '2')
        self.assertEqual(xml.attrib['max'], '12')
        self.assertEqual(xml[0].tag, 'label')
        self.assertEqual(xml[0].text, field.name)

    def test_serialize_truefalse_field(self):
        field = TrueFalseFieldFactory()
        serializer = ProjectFormSerializer()
        xml = serializer.serialize_truefalse_field(field)

        self.assertEqual(xml.tag, 'select1')
        self.assertEqual(xml.attrib['ref'], field.key)
        self.assertEqual(xml.attrib['required'], 'false')

        self.assertEqual(xml.find('label').text, field.name)
        self.assertEqual(len(xml.findall('item')), 2)

        for item in xml.findall('item'):
            self.assertIn(item.find('label').text, ['True', 'False'])
            if (item.find('label').text == 'True'):
                self.assertEqual(item.find('value').text, 'true')
            else:
                self.assertEqual(item.find('value').text, 'false')

    def test_serialize_required_truefalse_field(self):
        field = TrueFalseFieldFactory(**{'required': True})
        serializer = ProjectFormSerializer()
        xml = serializer.serialize_truefalse_field(field)

        self.assertEqual(xml.tag, 'select1')
        self.assertEqual(xml.attrib['ref'], field.key)
        self.assertEqual(xml.attrib['required'], 'true')


        # iterate through items and assert labels and values

    # def test_serialize_datetime_field(self):
    #     pass

    # def test_serialize_single_lookup_field(self):
    #     pass
