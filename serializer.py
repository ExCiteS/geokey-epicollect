from lxml import etree


class ProjectFormSerializer(object):
    def serialize_textfield(self, field):
        element = etree.Element(
            'input',
            ref=field.key,
            required=str(field.required).lower(),
            title='true',
            genkey='true'
        )

        label = etree.Element("label")
        label.text = field.name
        element.append(label)

        return element

    def serialize_numericfield(self, field):
        element = etree.Element(
            'input',
            ref=field.key,
            required=str(field.required).lower(),
            title='true',
            genkey='true',
            decimal='true'
        )

        if field.minval is not None:
            element.attrib['min'] = str(field.minval)
        if field.maxval is not None:
            element.attrib['max'] = str(field.maxval)

        label = etree.Element("label")
        label.text = field.name
        element.append(label)

        return element

    def create_item(self, label, value):
        item = etree.Element('item')

        labelEl = etree.Element("label")
        labelEl.text = label
        item.append(labelEl)

        valueEl = etree.Element("value")
        valueEl.text = value
        item.append(valueEl)

        return item

    def serialize_truefalse_field(self, field):
        element = etree.Element(
            'select1',
            ref=field.key,
            required=str(field.required).lower()
        )

        label = etree.Element("label")
        label.text = field.name
        element.append(label)

        element.append(self.create_item('True', 'true'))
        element.append(self.create_item('False', 'false'))
        return element
