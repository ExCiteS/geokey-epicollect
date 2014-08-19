"""
Serialises a Community Maps into EcML, an XML dialiect describing forms for
EpiCollect's mobile app.
"""
import calendar
from django.core.urlresolvers import reverse

from lxml import etree


class ProjectFormSerializer(object):
    # ########################################################################
    # Helpers
    # ########################################################################
    def create_label(self, field_name):
        """
        Creates a `<label>` element for a field
        """
        label = etree.Element('label')
        label.text = field_name
        return label

    def create_item(self, label, value):
        """
        Creates a `<item>` element. To used with select fields.
        """
        item = etree.Element('item')
        item.append(self.create_label(label))

        valueEl = etree.Element('value')
        valueEl.text = str(value)
        item.append(valueEl)

        return item

    def create_base_input(self, field):
        """
        Creates a basic `<input>` element for text, number and date inputs.
        Additional attributes can be added in the respective serializer
        methods.
        """
        base_input = etree.Element(
            'input',
            ref='%s_%s' % (field.key, field.observationtype.id)
        )

        if field.required:
            base_input.attrib['required'] = 'true'

        return base_input

    def create_base_select1(self, field):
        """
        Creates a basic `<select1>` element for lookups and true/false fields.
        Additional attributes can be added in the respective serializer
        methods.
        """
        base_select = etree.Element(
            'select1',
            ref='%s_%s' % (field.key, field.observationtype.id)
        )

        if field.required:
            base_select.attrib['required'] = 'true'

        return base_select

    # ########################################################################
    # Field serialisers
    # ########################################################################

    def serialize_textfield(self, field):
        """
        Serialises a TextField.
        """
        element = self.create_base_input(field)
        element.append(self.create_label(field.name))

        return element

    def serialize_numericfield(self, field):
        """
        Serialises a NumericField.
        """
        element = self.create_base_input(field)
        element.attrib['decimal'] = 'true'

        if field.minval is not None:
            element.attrib['min'] = str(field.minval)
        if field.maxval is not None:
            element.attrib['max'] = str(field.maxval)

        element.append(self.create_label(field.name))

        return element

    def serialize_truefalse_field(self, field):
        """
        Serialises a TrueFalseField.
        """
        element = self.create_base_select1(field)
        element.append(self.create_label(field.name))
        element.append(self.create_item('True', 'true'))
        element.append(self.create_item('False', 'false'))

        return element

    def serialize_singlelookup_field(self, field):
        """
        Serialises a LookupField.
        """
        element = self.create_base_select1(field)
        element.append(self.create_label(field.name))

        for value in field.lookupvalues.filter(status='active'):
            element.append(self.create_item(value.name, value.id))

        return element

    def serialize_datetime_field(self, field):
        """
        Serialises a DateTimeField.
        """
        element = self.create_base_input(field)
        element.attrib['date'] = 'dd/MM/yyyy'

        element.append(self.create_label(field.name))

        return element

    def serialize_field(self, field, jump_end):
        if field.fieldtype == 'TextField':
            field = self.serialize_textfield(field)
        elif field.fieldtype == 'NumericField':
            field = self.serialize_numericfield(field)
        elif field.fieldtype == 'TrueFalseField':
            field = self.serialize_truefalse_field(field)
        elif field.fieldtype == 'DateTimeField':
            field = self.serialize_datetime_field(field)
        elif field.fieldtype == 'LookupField':
            field = self.serialize_singlelookup_field(field)
        else:
            raise TypeError('Unknown field type.')

        if jump_end:
            field.attrib['jump'] = 'END,ALL'

        return field

    def serialize_observationtypes(self, observationtypes):
        form = etree.Element(
            'form',
            num='1',
            main='true'
        )

        observationtype_select = etree.Element(
            'select1',
            ref='contributiontype',
            required='true',
            jump=''
        )
        observationtype_select.append(self.create_label('Select type'))
        form.append(observationtype_select)

        for type_idx, observationtype in enumerate(observationtypes.all()):
            observationtype_select.append(
                self.create_item(observationtype.name, observationtype.id))

            for field_idx, field in enumerate(observationtype.fields.all()):
                if field_idx == 0:
                    jump = observationtype_select.attrib['jump']
                    if len(jump) == 0:
                        jump = ('%s_%s' % (field.key, field.observationtype.id)) + ',' + str(type_idx + 1)
                    else:
                        jump = jump + ',' + ('%s_%s' % (field.key, field.observationtype.id)) + ',' + str(type_idx + 1)
                    observationtype_select.attrib['jump'] = jump

                form.append(self.serialize_field(field, field_idx == (len(observationtype.fields.all()) - 1)))

        return form

    def serialize(self, project, base_url):
        root = etree.Element('ecml', version='1')

        model = etree.Element('model', version='1')
        model.append(etree.Element(
            'submission',
            id=str(project.id),
            projectName=project.name.replace(' ', '_'),
            allowDownloadEdits='false',
            versionNumber='2.1'
        ))

        upload = etree.Element('uploadToServer')
        upload.text = 'http://' + base_url + reverse(
            'epicollect:upload', kwargs={'project_id': project.id})
        model.append(upload)

        download = etree.Element('downloadFromServer')
        download.text = 'http://' + base_url + reverse(
            'epicollect:download', kwargs={'project_id': project.id})
        model.append(download)
        root.append(model)

        form = self.serialize_observationtypes(project.observationtypes.all())
        form.attrib['name'] = project.name.replace(' ', '_')
        form.attrib['key'] = 'unique_id'

        unique_id = etree.Element('input',
            required='true',
            title='true',
            genkey='true',
            ref='unique_id'
        )
        unique_id.append(self.create_label('Unique ID'))
        form.insert(0, unique_id)

        location = etree.Element('location', ref='location')
        location.append(self.create_label('Location'))
        form.insert(1, location)

        root.append(form)

        return root


class DataSerializer(object):
    def serialize_entry(self, observation):
        static_fields = [
            'unique_id', 'DeviceID', 'location_acc', 'location_provider',
            'location_alt', 'location_bearing'
        ]
        entry = etree.Element('entry')

        id = etree.Element('id')
        id.text = str(observation.id)
        entry.append(id)

        location_lon = created = etree.Element('location_lon')
        location_lon.text = str(observation.location.geometry.x)
        entry.append(location_lon)

        location_lat = created = etree.Element('location_lat')
        location_lat.text = str(observation.location.geometry.y)
        entry.append(location_lat)

        created = etree.Element('created')
        created.text = str(calendar.timegm(
            observation.created_at.utctimetuple()))
        entry.append(created)

        uploaded = etree.Element('uploaded')
        uploaded.text = observation.created_at.strftime('%Y-%m-%d %H:%M:%S')
        entry.append(uploaded)

        for key, value in observation.attributes.iteritems():
            tag_name = key
            if key not in static_fields:
                tag_name = tag_name + '_' + str(observation.observationtype.id) 
            el = etree.Element(tag_name)

            if value is not None and len(value) > 0:
                el.text = value
            else:
                el.text = 'Null'

            entry.append(el)

        return entry

    def serialize(self, project):
        root = etree.Element('entries')

        table = etree.Element('table')
        table_name = etree.Element('table_name')
        table_name.text = project.name.replace(' ', '_')

        table.append(table_name)
        root.append(table)

        for observation in project.observations.all():
            root.append(self.serialize_entry(observation))

        return root
