from lxml import etree


def xml_to_list(xml_string: str) -> list:
    """Parse the XML string of a list and extract the text values to a python list."""
    parser = etree.XMLParser()
    root = etree.XML(xml_string, parser)
    return [value.text for value in root]
