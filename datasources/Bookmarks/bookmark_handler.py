from lxml import etree as et
from pathlib import Path

from qgis.core import Qgis, QgsMessageLog


def import_bookmarks(source_bookmark_file: str, target_bookmark_file: str):
    """Imports spatial bookmarks from source to target profile.

    Spatial bookmarks are stored in bookmarks.xml, e.g.:
    <Bookmarks>
        <Bookmark id="..." group="" extent="POLYGON((...))" name="Test Bookmark">
            <spatialrefsys nativeFormat="Wkt">
            ...
            </spatialrefsys>
        </Bookmark>
        ...
    </Bookmarks>

    Args:
        TODO

    Returns:
        error_message (str): An error message, if something XML related failed.
    """
    # get the element tree of the source file
    QgsMessageLog.logMessage("import_bookmarks", "Profile Manager", level=Qgis.Critical)
    try:
        source_tree = et.parse(source_bookmark_file, et.XMLParser(remove_blank_text=True))

        # check if target file exists
        create_bookmark_file_if_not_exist(target_bookmark_file)
        # get the element tree of the target file
        # fill if empty
        target_tree = et.parse(target_bookmark_file, et.XMLParser(remove_blank_text=True))

        # find all bookmark elements
        source_root_tag = source_tree.findall('Bookmark')

        # get the root element "Bookmarks"
        target_tree_root = target_tree.getroot()

        # Remove duplicate entries to prevent piling data
        target_tree_root = remove_duplicates(source_root_tag, target_tree, target_tree_root)

        # append the elements
        for element in source_root_tag:
            target_tree_root.append(element)

        # overwrite the xml file
        et.ElementTree(target_tree_root).write(
            target_bookmark_file, pretty_print=True, encoding='utf-8', xml_declaration=True
        )
    except et.Error as e:
        # TODO: It would be nice to have a smaller and more specific try block but until then we except broadly
        error = f"{type(e)}: {str(e)}"
        QgsMessageLog.logMessage(error, "Profile Manager", level=Qgis.Warning)
        return error

def remove_duplicates(source_root_tag, target_tree, target_tree_root):
    """Removes bookmarks from target that exist in the (to be imported) source too."""
    # TODO FIXME this only checks the name of the bookmarks which will lead to false positives
    #            it is ok and supported by QGIS to have the same name for multiple bookmarks
    #            TODO compare the complete content of the xml node!
    target_root_tag = target_tree.findall('Bookmark')
    for s_element in source_root_tag:
        for t_element in target_root_tag:
            if s_element.attrib["name"] == t_element.attrib["name"]:
                target_tree_root.remove(t_element)

    return target_tree_root

def create_bookmark_file_if_not_exist(bookmark_file):
    """Checks if file exists and creates it if not"""
    target_file = Path(bookmark_file)
    if not target_file.is_file():
        with open(bookmark_file, "w") as new_file:
            new_file.write("<Bookmarks></Bookmarks>")

