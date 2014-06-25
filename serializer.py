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

    def serialize_numericfield(object, field):
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
