from xml.etree.ElementTree import XMLParser, XML


def xml_to_list(xml_string: str) -> list:
    """Parse the XML string of a list and extract the text values to a python list."""
    parser = XMLParser()
    root = XML(xml_string, parser)
    return [value.text for value in root]
