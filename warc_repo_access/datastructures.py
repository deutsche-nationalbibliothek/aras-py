from lxml import etree

def xml_to_list(xml_string: str) -> list:
    parser = etree.XMLParser()
    root = etree.XML(xml_string, parser)
    return [value.text for value in root]
