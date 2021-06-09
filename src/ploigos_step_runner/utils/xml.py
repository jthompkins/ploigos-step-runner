"""
Shared utils for dealing with XML.
"""

import glob
import re
import os.path
from xml.etree import ElementTree

def get_xml_element(xml_file, element_name):
    """ Gets a given element from a given xml file.

    Raises
    ------
    ValueError
        If the given xml_file does not exist.
        If the given xml_file does not contain an element with the given element_name.

    Returns
    -------
    xml.etree.ElementTree.Element
        The Element matching the given element_name.
    """

    # verify runtime config
    if not os.path.exists(xml_file):
        raise ValueError('Given xml file does not exist: ' + xml_file)

    # parse the xml file and figure out the namespace if there is one
    xml_xml = ElementTree.parse(xml_file)
    xml_root = xml_xml.getroot()
    xml_namespace_match = re.match(r'\{.*}', str(xml_root.tag))
    xml_namespace = ''
    if xml_namespace_match:
        xml_namespace = xml_namespace_match.group(0)

    # extract needed information from the xml file
    if xml_root.tag == element_name:
        xml_element = xml_root
    else:
        xml_element = xml_root.find('./' + xml_namespace + element_name)

    # verify information from xml file
    if xml_element is None:
        raise ValueError('Given xml file (' + \
             xml_file + \
             ') does not have ./' + \
             element_name + \
             ' element' \
        )

    return xml_element

def get_xml_element_by_path(xml_file_path, xpath, default_namespace=None, xml_namespace_dict=None):
    """Gets a given element from a given xml file given an xpath.

    Parameters
    ----------
    xml_file_path : str
        Path of the xml file
    xpath : str
        Xpath of the element you want
    default_namespace : str
        Optional string specifying the default namespace you are using in your xpath selector.
        This is the most common argument that will most likely be used.
        If your XML is namespaced, then even if your elements are in the default namespace,
        you must specify and use this namespace in both your xpath as well as specifying it here.
    xml_namespace_dict : Dict[str, str]
        Optional dictionary if default_namespace is not enough and you have multiple
        namespaces that you need to deal with in your xpath selector.

    Returns
    -------
    xml.etree.ElementTree.Element
        The Element found given the xpath
    """

    # verify runtime config
    if not os.path.exists(xml_file_path):
        raise ValueError(f'Given xml file does not exist: {xml_file_path}')

    xml_file = ElementTree.parse(xml_file_path).getroot()
    namespaces = xml_namespace_dict
    if xml_namespace_dict is None and default_namespace is not None:
        xml_namespace_match = re.findall(r'{(.*?)}', xml_file.tag)
        xml_namespace = xml_namespace_match[0] if xml_namespace_match else ''
        namespaces = {}
        namespaces[default_namespace] = xml_namespace

    if xml_namespace_dict is None and default_namespace is None:
        return xml_file.find(xpath)

    return xml_file.find(xpath, namespaces)

def aggregate_xml_element_attribute_values(xml_file_path, xml_element, attribs):
    """
    Function to parse a XML file looking for a specific element and obtaining its attributes.

    If element is not found in file the file is ignored.

    If attribute is not found in element the file is ignored.

    Parameters
    ----------
    xml_file_path: str
        Path to directory containing XML files
    xml_element: str
        XML element being searched for
    attribs: list
        List of attributes being searched for in the XML element

    Returns: 
    
    report_results: dict
        A dictionary of attribute values.

    Raises
    ------
    ValueError
        If XML element is not found in file(s)

    """

    report_results = {}

    #Search file path for XML files

    if os.path.isdir(xml_file_path):
        xml_files = glob.glob(xml_file_path + '/*.xml', recursive=False)
    elif os.path.isfile(xml_file_path):
        xml_files = [xml_file_path]

    print("files: " + str(xml_files))

    print("file exists: " +str(os.path.isfile(xml_files[0])))
    with open(xml_files[0], "r") as f:
        print("line: " + f.read())

    #Iterate over XML files
    for file in xml_files:
       
        try:
            pom_element = get_xml_element(file, xml_element)
            #Add attributes to dictionary
            for attrib in attribs:
                if attrib in pom_element.attrib:
                    attribute_value = pom_element.attrib[attrib]
                    # aggregate attribute accross multiple files
                    if attrib in report_results:
                        report_results[attrib] = str(float(report_results[attrib]) + float(attribute_value))
                    else:
                        report_results[attrib] = attribute_value
                else:
                    pass
        except ValueError:
            pass
     
        

    return report_results
