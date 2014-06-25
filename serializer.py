from lxml import etree


class ProjectFormSerializer(object):
    def serialize_textfield(self, textfield):
        element = etree.Element(
            'input',
            ref=textfield.key,
            required=str(textfield.required).lower(),
            title='true',
            genkey='true'
        )

        label = etree.Element("label")
        label.text = textfield.name
        element.append(label)

        return element
