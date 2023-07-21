from configparser import RawConfigParser
from re import compile, search
from urllib.parse import unquote

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QTreeWidgetItem
from qgis.core import Qgis, QgsMessageLog


# TODO document these!
SERVICE_NAME_REGEX = compile(r'\\(.*?)\\')
GPKG_SERVICE_NAME_REGEX = compile(r'\\(.+).\\')


def gather_data_source_connections(ini_path: str, compile_string: str) -> list[str]:
    """Returns a list of data source connection names matching the search string in the INI file.

    Args:
        ini_path (str): Path to the INI file to read
        compile_string (str): Regex for searching corresponding data sources in INI file

    Returns:
        list[str]: List of found data source connections
    """
    ini_parser = RawConfigParser()
    ini_parser.optionxform = str  # str = case-sensitive option names
    ini_parser.read(ini_path)

    try:
        # the connections are inside the qgis section # TODO not always true, we need to check other places too!
        section = ini_parser['qgis']
    except KeyError:
        return None

    data_source_connections = []
    search_string = compile(compile_string)
    for key in section:
        if search_string.search(key):
            source_name_raw = search(SERVICE_NAME_REGEX, key)
            # TODO why this replacement here? ->
            source_name = source_name_raw.group(0).replace("\\", "")
            # TODO "Bing VirtualEarth 💩" is not rendered well, also fails to import to other profile...
            source_name = unquote(source_name, 'latin-1')  # needed for e.g. %20 in connection names
            data_source_connections.append(source_name)

    return data_source_connections

def get_data_sources_tree(ini_path: str, compile_string: str, tree_name: str, make_checkable: bool) -> QTreeWidgetItem:
    """Returns a tree of checkable items for all data sources matching the search string in the INI file.

    The tree contains a checkable item per data source found.

    Args:
        ini_path (str): Path to the INI file to read
        compile_string (str): Regex for searching corresponding data sources in INI file
        tree_name (str): Name of the parent tree item (e.g. "WMS")
        make_checkable (bool): Flag to indicate if items should be checkable

    Returns:
        QTreeWidgetItem: Tree widget item representing the data sources or None if none were found
    """
    data_source_connections = gather_data_source_connections(ini_path, compile_string)
    if not data_source_connections:
        QgsMessageLog.logMessage(f"- 0 {tree_name} connections found", "Profile Manager", Qgis.Info)
        return None
    else:
        QgsMessageLog.logMessage(
            f"- {len(data_source_connections)} {tree_name} connections found", "Profile Manager", Qgis.Info
        )

    tree_root_item = QTreeWidgetItem([tree_name])
    if make_checkable:
        tree_root_item.setFlags(tree_root_item.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

    data_source_items = []
    for data_source_connection in data_source_connections:
        data_source_item = QTreeWidgetItem([data_source_connection])
        if make_checkable:
            data_source_item.setFlags(data_source_item.flags() | Qt.ItemIsUserCheckable)
            data_source_item.setCheckState(0, Qt.Unchecked)
        data_source_items.append(data_source_item)

    tree_root_item.addChildren(data_source_items)
    return tree_root_item

def gather_db_data_source_connections(ini_path: str, section: str, compile_string: str) -> list[str]:
    """Returns a list of DB data source connection names matching the search string in the INI file.

    Args:
        ini_path (str): Path to the INI file to read
        section (str): The section of the INI file to search through
        compile_string (str): Regex for searching corresponding data sources in INI section

    Returns:
        list[str]: List of found data source connections
    """
    # TODO unify with gather_data_source_connections
    ini_parser = RawConfigParser()
    ini_parser.optionxform = str  # str = case-sensitive option names
    ini_parser.read(ini_path)

    try:
        section = ini_parser[section]
    except KeyError:
        return None

    db_data_source_connections = []
    search_string = compile(compile_string)
    for key in section:
        if search_string.search(key):
            # ugly hack to use the section="providers" to check if we are looking for GeoPackages just
            # to drop the tree_name parameter, but for now this will do...
            # TODO use some better logic, i.e. specify the connection type at the caller and store the regex/logic HERE!
            if section == "providers":
                source_name_raw = search(GPKG_SERVICE_NAME_REGEX, key)
                source_name = source_name_raw.group(0).replace("\\GPKG\\connections\\", "").replace("\\", "")
            else:
                source_name_raw = search(SERVICE_NAME_REGEX, key)
                source_name = source_name_raw.group(0).replace("\\", "")
                # TODO what are the replacements needed for?!

            # TODO see get_data_sources_tree
            source_name = unquote(source_name, 'latin-1')
            db_data_source_connections.append(source_name)

    return db_data_source_connections

def get_db_sources_tree(ini_path, compile_string, tree_name, section, make_checkable):
    """Returns a tree of checkable items for all data sources matching the search string in the INI file.

    The tree contains a checkable item per data source found.

    Args:
        ini_path (str): Path to the INI file to read
        compile_string (str): Regex for searching corresponding data sources in INI file
        section (str): The section of the INI file to search through
        tree_name (str): Name of the parent tree item (e.g. "WMS")
        make_checkable (bool): Flag to indicate if items should be checkable

    Returns:
        QTreeWidgetItem: Tree widget item representing the data sources or None if none were found
    """
    data_source_connections = gather_db_data_source_connections(ini_path, section, compile_string)
    if not data_source_connections:
        QgsMessageLog.logMessage(f"- 0 {tree_name} connections found", "Profile Manager", Qgis.Info)
        return None
    else:
        QgsMessageLog.logMessage(
            f"- {len(data_source_connections)} {tree_name} connections found", "Profile Manager", Qgis.Info
        )

    tree_root_item = QTreeWidgetItem([tree_name])
    if make_checkable:
        tree_root_item.setFlags(tree_root_item.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

    data_source_items = []
    for data_source_connection in data_source_connections:
        data_source_item = QTreeWidgetItem([data_source_connection])
        if make_checkable:
            data_source_item.setFlags(data_source_item.flags() | Qt.ItemIsUserCheckable)
            data_source_item.setCheckState(0, Qt.Unchecked)
        data_source_items.append(data_source_item)

    tree_root_item.addChildren(data_source_items)
    return tree_root_item
