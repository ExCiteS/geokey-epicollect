from lxml import etree
from django.test import TestCase

from ..serializer import ProjectFormSerializer
from observationtypes.tests.model_factories import (
    TextFieldFactory, NumericFieldFactory, TrueFalseFieldFactory,
    LookupFieldFactory, LookupValueFactory, DateTimeFieldFactory
)


class ProjectFormSerializerTest(TestCase):
    # ########################################################################
    # Test helpers
    # ########################################################################
    def test_create_item(self):
        serializer = ProjectFormSerializer()
        item = serializer.create_item('True', 'true')
        self.assertEqual(item.find('value').text, 'true')
        self.assertEqual(item.find('label').text, 'True')

    def test_create_label(self):
        serializer = ProjectFormSerializer()
        label = serializer.create_label('Field name')

        self.assertEqual(label.tag, 'label')
        self.assertEqual(label.text, 'Field name')

    def test_create_base_input(self):
        serializer = ProjectFormSerializer()

        field = TextFieldFactory()
        xml = serializer.create_base_input(field)

        self.assertEqual(xml.tag, 'input')
        self.assertEqual(xml.attrib['ref'], field.key)
        self.assertEqual(xml.attrib['required'], 'false')

        field = TextFieldFactory(**{'required': True})
        xml = serializer.create_base_input(field)

        self.assertEqual(xml.tag, 'input')
        self.assertEqual(xml.attrib['ref'], field.key)
        self.assertEqual(xml.attrib['required'], 'true')

    def test_create_base_select1(self):
        serializer = ProjectFormSerializer()

        field = TrueFalseFieldFactory()
        xml = serializer.create_base_select1(field)

        self.assertEqual(xml.tag, 'select1')
        self.assertEqual(xml.attrib['ref'], field.key)
        self.assertEqual(xml.attrib['required'], 'false')

        field = TrueFalseFieldFactory(**{'required': True})
        xml = serializer.create_base_select1(field)

        self.assertEqual(xml.tag, 'select1')
        self.assertEqual(xml.attrib['ref'], field.key)
        self.assertEqual(xml.attrib['required'], 'true')

    # ########################################################################
    # Test serializers
    # ########################################################################

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
            xml.attrib['date']

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

        with self.assertRaises(KeyError):
            xml.attrib['date']
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
            xml.attrib['date']

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
            xml.attrib['date']

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

        with self.assertRaises(KeyError):
            xml.attrib['date']

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
            self.assertIn(item.find('value').text, ['true', 'false'])

    def test_serialize_single_lookup_field(self):
        field = LookupFieldFactory()
        val1 = LookupValueFactory(**{'field': field, 'name': 'Kermit'})
        val2 = LookupValueFactory(**{'field': field, 'name': 'Ms. Piggy'})
        val3 = LookupValueFactory(**{'field': field, 'name': 'Gonzo'})

        serializer = ProjectFormSerializer()
        xml = serializer.serialize_singlelookup_field(field)

        self.assertEqual(xml.tag, 'select1')
        self.assertEqual(xml.attrib['ref'], field.key)
        self.assertEqual(xml.attrib['required'], 'false')
        self.assertEqual(len(xml.findall('item')), 3)

        for item in xml.findall('item'):
            self.assertIn(
                item.find('label').text,
                [val1.name, val2.name, val3.name]
            )
            self.assertIn(
                item.find('value').text,
                [str(val1.id), str(val2.id), str(val3.id)]
            )

    def test_serialize_datetime_field(self):
        field = DateTimeFieldFactory()
        serializer = ProjectFormSerializer()
        xml = serializer.serialize_datetime_field(field)

        self.assertEqual(xml.tag, 'input')
        self.assertEqual(xml.attrib['ref'], field.key)
        self.assertEqual(xml.attrib['required'], 'false')
        self.assertEqual(xml.attrib['date'], 'dd/MM/yyyy')
        self.assertEqual(xml[0].tag, 'label')
        self.assertEqual(xml[0].text, field.name)

        with self.assertRaises(KeyError):
            xml.attrib['min']
            xml.attrib['max']
            xml.attrib['decimal']
