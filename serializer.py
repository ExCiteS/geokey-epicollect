"""
Serialises a Community Maps into EcML, an XML dialiect describing forms for
EpiCollect's mobile app.
"""
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
        return etree.Element(
            'input',
            ref=field.key,
            required=str(field.required).lower(),
        )

    def create_base_select1(self, field):
        """
        Creates a basic `<select1>` element for lookups and true/false fields.
        Additional attributes can be added in the respective serializer
        methods.
        """
        return etree.Element(
            'select1',
            ref=field.key,
            required=str(field.required).lower()
        )

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

    def serialize_field(self, field):
        if field.fieldtype == 'TextField':
            return self.serialize_textfield(field)
        elif field.fieldtype == 'NumericField':
            return self.serialize_numericfield(field)
        elif field.fieldtype == 'TrueFalseField':
            return self.serialize_truefalse_field(field)
        elif field.fieldtype == 'DateTimeField':
            return self.serialize_datetime_field(field)
        elif field.fieldtype == 'LookupField':
            return self.serialize_singlelookup_field(field)
        else:
            raise TypeError('Unknown field type.')

    def serialize_observationtypes(self, observationtypes):
        form = etree.Element(
            'form',
            num='1',
            main='true'
        )

        observationtype_select = etree.Element(
            'select1',
            ref='observationtype',
            required='true',
            jump=''
        )
        form.append(observationtype_select)

        for type_idx, observationtype in enumerate(observationtypes.all()):
            observationtype_select.append(
                self.create_item(observationtype.name, observationtype.id))

            for field_idx, field in enumerate(observationtype.fields.all()):
                if field_idx == 0:
                    jump = observationtype_select.attrib['jump']
                    if len(jump) == 0:
                        jump = field.key + ',' + str(type_idx + 1)
                    else:
                        jump = jump + ',' + field.key + ',' + str(type_idx + 1)
                    observationtype_select.attrib['jump'] = jump

                form.append(self.serialize_field(field))

        return form

    def serialize(self, project, base_url):
        root = etree.Element('ecml', version='1')

        model = etree.Element('model', version='1')
        model.append(etree.Element(
            'submission',
            id=str(project.id),
            projectName=project.name,
            allowDownloadEdits='false',
            versionNumber='2.1'
        ))

        upload = etree.Element('uploadToServer')
        upload.text = base_url + reverse(
            'epicollect:upload', kwargs={'project_id': project.id})
        model.append(upload)

        download = etree.Element('downloadFromServer')
        download.text = base_url + reverse(
            'epicollect:download', kwargs={'project_id': project.id})
        model.append(download)
        root.append(model)

        form = self.serialize_observationtypes(project.observationtypes.all())
        form.attrib['name'] = str(project.id)
        form.attrib['id'] = str(project.id)

        location = etree.Element('location', ref='location')
        location.append(self.create_label('Location'))
        form.insert(0, location)

        root.append(form)

        return root
