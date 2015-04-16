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
        key = field.key.replace('-', '_')
        base_input = etree.Element(
            'input',
            ref='%s_%s' % (key, field.category.id)
        )

        if field.required:
            base_input.attrib['required'] = 'true'

        return base_input

    def create_base_select(self, field, type):
        """
        Creates a basic `<radio>` element for lookups and true/false fields.
        Additional attributes can be added in the respective serializer
        methods.
        """
        key = field.key.replace('-', '_')
        base_select = etree.Element(
            type,
            ref='%s_%s' % (key, field.category.id)
        )

        if field.required:
            base_select.attrib['required'] = 'true'

        return base_select

    def get_photo_input(self):
        photo = etree.Element('photo', ref='photo')
        photo.append(self.create_label('Add photo'))
        return photo

    def get_video_input(self):
        photo = etree.Element('video', ref='video')
        photo.append(self.create_label('Add video'))
        return photo

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

    def serialize_singlelookup_field(self, field):
        """
        Serialises a LookupField.
        """
        element = self.create_base_select(field, 'radio')
        element.append(self.create_label(field.name))

        for value in field.lookupvalues.filter(status='active'):
            element.append(self.create_item(value.name, value.id))

        return element

    def serialize_multiplelookup_field(self, field):
        """
        Serialises a MultipleLookupField.
        """
        element = self.create_base_select(field, 'select')
        element.append(self.create_label(field.name))

        for value in field.lookupvalues.filter(status='active'):
            element.append(self.create_item(value.name, value.id))

        return element

    def serialize_date_field(self, field):
        """
        Serialises a DateField or DateTimeField.
        """
        element = self.create_base_input(field)
        element.attrib['date'] = 'dd/MM/yyyy'

        element.append(self.create_label(field.name))

        return element

    def serialize_time_field(self, field):
        """
        Serialises a DateField or DateTimeField.
        """
        element = self.create_base_input(field)
        element.attrib['time'] = 'HH:mm'

        element.append(self.create_label(field.name))

        return element

    def serialize_field(self, field, jump_end):
        if field.fieldtype == 'TextField':
            field = self.serialize_textfield(field)
        elif field.fieldtype == 'NumericField':
            field = self.serialize_numericfield(field)
        elif (field.fieldtype == 'DateTimeField' or
                field.fieldtype == 'DateField'):
            field = self.serialize_date_field(field)
        elif field.fieldtype == 'TimeField':
            field = self.serialize_time_field(field)
        elif field.fieldtype == 'LookupField':
            field = self.serialize_singlelookup_field(field)
        elif field.fieldtype == 'MultipleLookupField':
            field = self.serialize_multiplelookup_field(field)
        else:
            raise TypeError('Unknown field type.')

        if jump_end:
            field.attrib['jump'] = 'photo,ALL'

        return field

    def serialize_categories(self, categories):
        form = etree.Element(
            'form',
            num='1',
            main='true'
        )

        category_select = etree.Element(
            'select1',
            ref='category',
            required='true',
            jump=''
        )
        category_select.append(self.create_label('Select type'))
        form.append(category_select)

        for type_idx, category in enumerate(categories):
            category_select.append(
                self.create_item(category.name, category.id))

            for field_idx, field in enumerate(category.fields.filter(
                    status='active')):
                if type_idx > 0 and field_idx == 0:
                    field_key = field.key.replace('-', '_')
                    jump = category_select.attrib['jump']
                    if len(jump) == 0:
                        jump = ('%s_%s,%s' % (
                            field_key,
                            field.category.id,
                            str(type_idx + 1)
                        ))
                    else:
                        jump = jump + ',' + ('%s_%s,%s' % (
                            field_key,
                            field.category.id,
                            str(type_idx + 1)
                        ))
                    category_select.attrib['jump'] = jump

                form.append(self.serialize_field(
                    field, field_idx == (len(category.fields.all()) - 1)
                ))

        return form

    def serialize(self, project, base_url):
        root = etree.Element('ecml', version='1')

        model = etree.Element('model', version='1')
        model.append(etree.Element(
            'submission',
            id=str(project.id),
            projectName=project.name.replace(' ', '_').lower(),
            allowDownloadEdits='false',
            versionNumber='2.1'
        ))

        upload = etree.Element('uploadToServer')
        upload.text = 'http://' + base_url + reverse(
            'geokey_epicollect:upload', kwargs={'project_id': project.id})
        model.append(upload)

        download = etree.Element('downloadFromServer')
        download.text = 'http://' + base_url + reverse(
            'geokey_epicollect:download', kwargs={'project_id': project.id})
        model.append(download)
        root.append(model)

        form = self.serialize_categories(
            project.categories.filter(status='active')
        )
        form.attrib['name'] = project.name.replace(' ', '_')
        form.attrib['key'] = 'unique_id'

        form.append(self.get_photo_input())
        form.append(self.get_video_input())

        unique_id = etree.Element(
            'input',
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
    static_fields = [
        'unique_id', 'DeviceID', 'location_acc', 'location_provider',
        'location_alt', 'location_bearing'
    ]

    def serialize_entry_to_xml(self, observation):
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

        for key, value in observation.properties.iteritems():
            tag_name = key.replace('-', '_')
            if key not in self.static_fields:
                tag_name = tag_name + '_' + str(observation.category.id)
            el = etree.Element(tag_name)

            if value is not None and len(value) > 0:
                el.text = value
            else:
                el.text = 'Null'

            entry.append(el)

        return entry

    def serialize_to_xml(self, project):
        root = etree.Element('entries')

        table = etree.Element('table')
        table_name = etree.Element('table_name')
        table_name.text = project.name.replace(' ', '_')

        table.append(table_name)
        root.append(table)

        for observation in project.observations.all():
            root.append(self.serialize_entry_to_xml(observation))

        return root

    def serialize_entry_to_tsv(self, observation):
        line = observation.project.name.replace(' ', '_') + '\t'

        line = line + 'id\t' + str(observation.id) + '\t'
        line = line + 'location_lon\t' + str(observation.location.geometry.x) + '\t'
        line = line + 'location_lat\t' + str(observation.location.geometry.y) + '\t'
        line = line + 'created\t' + str(calendar.timegm(observation.created_at.utctimetuple())) + '\t'
        line = line + 'uploaded\t' + observation.created_at.strftime('%Y-%m-%d %H:%M:%S') + '\t'

        for key, value in observation.properties.iteritems():
            tag_name = key.replace('-', '_')
            if key not in self.static_fields:
                tag_name = tag_name + '_' + str(observation.category.id)

            val = value
            if value is None or len(value) == 0:
                val = 'Null'

            line = line + tag_name + '\t' + val + '\t'

        return line + '\n'

    def serialize_to_tsv(self, project):
        tsv = ''

        for observation in project.observations.all():
            tsv = tsv + self.serialize_entry_to_tsv(observation)

        return tsv
