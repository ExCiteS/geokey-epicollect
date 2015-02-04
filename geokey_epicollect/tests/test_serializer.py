from lxml import etree
import calendar
from django.test import TestCase

from ..serializer import ProjectFormSerializer, DataSerializer
from categories.tests.model_factories import (
    TextFieldFactory, NumericFieldFactory, DateFieldFactory, TimeFieldFactory,
    LookupFieldFactory, LookupValueFactory, DateTimeFieldFactory,
    MultipleLookupFieldFactory, MultipleLookupValueFactory
)

from projects.tests.model_factories import ProjectF
from categories.tests.model_factories import CategoryFactory
from contributions.tests.model_factories import ObservationFactory


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
        self.assertEqual(
            xml.attrib['ref'],
            field.key + '_' + str(field.category.id)
        )

        field = TextFieldFactory(**{'required': True})
        xml = serializer.create_base_input(field)

        self.assertEqual(xml.tag, 'input')
        self.assertEqual(
            xml.attrib['ref'],
            field.key + '_' + str(field.category.id)
        )
        self.assertEqual(xml.attrib['required'], 'true')

    def test_create_base_select(self):
        serializer = ProjectFormSerializer()

        field = LookupFieldFactory()
        xml = serializer.create_base_select(field, 'radio')

        self.assertEqual(xml.tag, 'radio')
        self.assertEqual(
            xml.attrib['ref'],
            field.key + '_' + str(field.category.id)
        )

        field = LookupFieldFactory(**{'required': True})
        xml = serializer.create_base_select(field, 'radio')

        self.assertEqual(xml.tag, 'radio')
        self.assertEqual(
            xml.attrib['ref'],
            field.key + '_' + str(field.category.id)
        )
        self.assertEqual(xml.attrib['required'], 'true')

    # ########################################################################
    # Test serializers
    # ########################################################################

    def test_serialize_textfield(self):
        field = TextFieldFactory()
        serializer = ProjectFormSerializer()
        xml = serializer.serialize_textfield(field)

        self.assertEqual(xml.tag, 'input')
        self.assertEqual(
            xml.attrib['ref'],
            field.key + '_' + str(field.category.id)
        )

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
        self.assertEqual(
            xml.attrib['ref'],
            field.key + '_' + str(field.category.id)
        )

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
        self.assertEqual(
            xml.attrib['ref'],
            field.key + '_' + str(field.category.id)
        )
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
        self.assertEqual(
            xml.attrib['ref'],
            field.key + '_' + str(field.category.id)
        )
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
        self.assertEqual(
            xml.attrib['ref'],
            field.key + '_' + str(field.category.id)
        )
        self.assertEqual(xml.attrib['required'], 'true')
        self.assertEqual(xml.attrib['decimal'], 'true')
        self.assertEqual(xml.attrib['min'], '2')
        self.assertEqual(xml.attrib['max'], '12')
        self.assertEqual(xml[0].tag, 'label')
        self.assertEqual(xml[0].text, field.name)

        with self.assertRaises(KeyError):
            xml.attrib['date']

    def test_serialize_single_lookup_field(self):
        field = LookupFieldFactory()
        val1 = LookupValueFactory(**{'field': field, 'name': 'Kermit'})
        val2 = LookupValueFactory(**{'field': field, 'name': 'Ms. Piggy'})
        val3 = LookupValueFactory(**{'field': field, 'name': 'Gonzo'})

        serializer = ProjectFormSerializer()
        xml = serializer.serialize_singlelookup_field(field)

        self.assertEqual(xml.tag, 'radio')
        self.assertEqual(
            xml.attrib['ref'],
            field.key + '_' + str(field.category.id)
        )
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

    def test_serialize_multiple_lookup_field(self):
        field = MultipleLookupFieldFactory()
        val1 = MultipleLookupValueFactory(**{'field': field, 'name': 'Kermit'})
        val2 = MultipleLookupValueFactory(
            **{'field': field, 'name': 'Ms. Piggy'}
        )
        val3 = MultipleLookupValueFactory(**{'field': field, 'name': 'Gonzo'})

        serializer = ProjectFormSerializer()
        xml = serializer.serialize_multiplelookup_field(field)

        self.assertEqual(xml.tag, 'select')
        self.assertEqual(
            xml.attrib['ref'],
            field.key + '_' + str(field.category.id)
        )
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

    def test_serialize_date_field(self):
        field = DateFieldFactory()
        serializer = ProjectFormSerializer()
        xml = serializer.serialize_date_field(field)

        self.assertEqual(xml.tag, 'input')
        self.assertEqual(
            xml.attrib['ref'],
            field.key + '_' + str(field.category.id)
        )
        self.assertEqual(xml.attrib['date'], 'dd/MM/yyyy')
        self.assertEqual(xml[0].tag, 'label')
        self.assertEqual(xml[0].text, field.name)

        with self.assertRaises(KeyError):
            xml.attrib['min']
            xml.attrib['max']
            xml.attrib['decimal']

    def test_serialize_time_field(self):
        field = TimeFieldFactory()
        serializer = ProjectFormSerializer()
        xml = serializer.serialize_time_field(field)
        self.assertEqual(xml.tag, 'input')
        self.assertEqual(
            xml.attrib['ref'],
            field.key + '_' + str(field.category.id)
        )
        self.assertEqual(xml.attrib['time'], 'HH:mm')
        self.assertEqual(xml[0].tag, 'label')
        self.assertEqual(xml[0].text, field.name)

        with self.assertRaises(KeyError):
            xml.attrib['min']
            xml.attrib['max']
            xml.attrib['decimal']

    def test_serialize_datetime_field(self):
        field = DateTimeFieldFactory()
        serializer = ProjectFormSerializer()
        xml = serializer.serialize_date_field(field)

        self.assertEqual(xml.tag, 'input')
        self.assertEqual(
            xml.attrib['ref'],
            field.key + '_' + str(field.category.id)
        )
        self.assertEqual(xml.attrib['date'], 'dd/MM/yyyy')
        self.assertEqual(xml[0].tag, 'label')
        self.assertEqual(xml[0].text, field.name)

        with self.assertRaises(KeyError):
            xml.attrib['min']
            xml.attrib['max']
            xml.attrib['decimal']

    def test_serialize_project(self):
        project = ProjectF()
        type1 = CategoryFactory.create(**{'project': project})
        TextFieldFactory(**{'category': type1})
        type2 = CategoryFactory.create(**{'project': project})
        TextFieldFactory(**{'category': type2})
        type3 = CategoryFactory.create(**{'project': project})
        TextFieldFactory(**{'category': type3})
        serializer = ProjectFormSerializer()
        xml = serializer.serialize(project, 'http://192.168.57.10:8000')

        self.assertEqual(
            xml.find('model').find('submission').attrib['id'], str(project.id)
        )
        self.assertEqual(
            xml.find('model').find('submission').attrib['projectName'],
            project.name.replace(' ', '_')
        )
        # self.assertEqual(
        #     xml.find('model').find('uploadToServer').text,
        #     'http://192.168.57.10:8000/epicollect/projects/%s/upload/' %
        #     project.id
        # )
        # self.assertEqual(
        #     xml.find('model').find('downloadFromServer').text,
        #     'http://192.168.57.10:8000/epicollect/projects/%s/download/' %
        #     project.id
        # )
        self.assertEqual(
            xml.find('form').find('location').find('label').text,
            'Location'
        )


class SerializeDataTest(TestCase):
    def test_serialize_observation(self):
        observation = ObservationFactory.create()
        observation.attributes = {'thekey': '46'}

        serializer = DataSerializer()
        xml = serializer.serialize_entry_to_xml(observation)

        self.assertEqual(str(observation.id), xml.find('id').text)
        self.assertEqual(
            str(calendar.timegm(observation.created_at.utctimetuple())),
            xml.find('created').text)
        self.assertEqual(
            observation.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            xml.find('uploaded').text
        )

    def test_serialize_all_to_xml(self):
        number = 20
        project = ProjectF.create(**{'isprivate': False})
        ObservationFactory.create_batch(
            number, **{'project': project, 'attributes': {'key': 'value'}}
        )

        serializer = DataSerializer()
        xml = serializer.serialize_to_xml(project)

        self.assertEqual(len(xml.findall('entry')), number)

    def test_serialize_all_to_tsv(self):
        number = 20
        project = ProjectF.create(**{'isprivate': False})
        ObservationFactory.create_batch(
            number, **{'project': project, 'attributes': {'key': 'value'}}
        )

        serializer = DataSerializer()
        tsv = serializer.serialize_to_tsv(project)
        self.assertEqual(20, tsv.count('\n'))
