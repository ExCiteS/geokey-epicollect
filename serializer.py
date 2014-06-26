from lxml import etree


class ProjectFormSerializer(object):
    def create_label(self, field_name):
        label = etree.Element('label')
        label.text = field_name
        return label

    def create_item(self, label, value):
        item = etree.Element('item')
        item.append(self.create_label(label))

        valueEl = etree.Element('value')
        valueEl.text = str(value)
        item.append(valueEl)

        return item

    def create_base_input(self, field):
        return etree.Element(
            'input',
            ref=field.key,
            required=str(field.required).lower(),
        )

    def create_base_select1(self, field):
        return etree.Element(
            'select1',
            ref=field.key,
            required=str(field.required).lower()
        )

    def serialize_textfield(self, field):
        element = self.create_base_input(field)
        element.append(self.create_label(field.name))

        return element

    def serialize_numericfield(self, field):
        element = self.create_base_input(field)
        element.attrib['decimal'] = 'true'

        if field.minval is not None:
            element.attrib['min'] = str(field.minval)
        if field.maxval is not None:
            element.attrib['max'] = str(field.maxval)

        element.append(self.create_label(field.name))

        return element

    def serialize_truefalse_field(self, field):
        element = self.create_base_select1(field)
        element.append(self.create_label(field.name))
        element.append(self.create_item('True', 'true'))
        element.append(self.create_item('False', 'false'))

        return element

    def serialize_singlelookup_field(self, field):
        element = self.create_base_select1(field)
        element.append(self.create_label(field.name))

        for value in field.lookupvalues.filter(status='active'):
            element.append(self.create_item(value.name, value.id))

        return element

    def serialize_datetime_field(self, field):
        element = self.create_base_input(field)
        element.attrib['date'] = 'dd/MM/yyyy'

        element.append(self.create_label(field.name))

        return element
