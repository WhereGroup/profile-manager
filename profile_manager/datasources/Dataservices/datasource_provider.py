from configparser import RawConfigParser
from re import compile, search
from urllib.parse import unquote

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QTreeWidgetItem
from qgis.core import Qgis, QgsMessageLog


# TODO document these! can we directly integrate them below somewhere?
SERVICE_NAME_REGEX = compile(r'\\(.*?)\\')
GPKG_SERVICE_NAME_REGEX = compile(r'\\(.+).\\')

"""
"providername-ish": [  # a list of searching rules, not just one, because qgis changed between versions
    {
        "section": "section_to_search",  # INI section in which to search for regex matches
        "regex": "<°((^(-<",  # regex to search for in the keys of the section
    },
]
# TODO document the versions of QGIS that are using a specific rule
"""
DATA_SOURCE_SEARCH_LOCATIONS = {
    "GeoPackage": [
        {
            "section": "providers",
            "regex": "^ogr.GPKG.connections.*path",
        },
    ],
    "SpatiaLite": [
        {
            "section": "SpatiaLite",
            "regex": "^connections.*sqlitepath",
        },
    ],
    "PostgreSQL": [
        {
            "section": "PostgreSQL",
            "regex": "^connections.*host",
        },
    ],
    "MSSQL": [
        {
            "section": "MSSQL",
            "regex": "^connections.*host",
        },
    ],
    "DB2": [
        {
            "section": "DB2",
            "regex": "^connections.*host",
        },
    ],
    "Oracle": [
        {
            "section": "Oracle",
            "regex": "^connections.*host",
        },
    ],
    "Vector-Tile": [
        {
            "section": "qgis",
            "regex": "^connections-vector-tile.*url",
        },
    ],
    "WMS": [
        {
            "section": "qgis",
            "regex": "^connections-wms.*url",
        },
    ],
    "WFS": [
        {
            "section": "qgis",
            "regex": "^connections-wfs.*url",
        },
    ],
    "WCS": [
        {
            "section": "qgis",
            "regex": "^connections-wcs.*url",
        },
    ],
    "XYZ": [
        {
            "section": "qgis",
            "regex": "^connections-xyz.*url",
        },
    ],
    "ArcGisMapServer": [
        {
            "section": "qgis",
            "regex": "^connections-arcgismapserver.*url",
        },
    ],
    "ArcGisFeatureServer": [
        {
            "section": "qgis",
            "regex": "^connections-arcgisfeatureserver.*url",
        },
    ],
    # TODO GeoNode was a core plugin once TODO document?
    "GeoNode": [
        {
            "section": "qgis",
            "regex": "^connections-geonode.*url",
        },
    ],
}


def get_data_sources_tree(ini_path: str, provider: str, make_checkable: bool) -> QTreeWidgetItem:
    """Returns a tree of checkable items for all data sources of the specified provider in the INI file.

    The tree contains a checkable item per data source found.

    Args:
        ini_path (str): Path to the INI file to read
        provider (str): Name of the provider to gather data sources for
        make_checkable (bool): Flag to indicate if items should be checkable

    Returns:
        QTreeWidgetItem: Tree widget item representing the data sources or None if none were found
    """
    data_source_connections = gather_data_source_connections(ini_path, provider)
    if not data_source_connections:
        QgsMessageLog.logMessage(f"- 0 {provider} connections found", "Profile Manager", Qgis.Info)
        return None
    else:
        QgsMessageLog.logMessage(
            f"- {len(data_source_connections)} {provider} connections found", "Profile Manager", Qgis.Info
        )

    tree_root_item = QTreeWidgetItem([provider])
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

def gather_data_source_connections(ini_path: str, provider: str) -> list[str]:
    """Returns the names of all data source connections of the specified provider in the INI file.

    Args:
        ini_path (str): Path to the INI file to read
        provider (str): Name of the provider to gather connections of

    Returns:
        list[str]: Names of the found data source connections

    Raises:
        NotImplementedError: If the provider name is not (yet) known here
    """
    search_rules = DATA_SOURCE_SEARCH_LOCATIONS.get(provider)
    if not search_rules:
        raise NotImplementedError(f"Unknown provider: {provider}")

    # TODO make iterating if more than 1 rule was found
    # TODO how to handle multiple finds? deduplicate?
    section_to_search = search_rules[0]["section"]
    regex = search_rules[0]["regex"]

    ini_parser = RawConfigParser()
    ini_parser.optionxform = str  # str = case-sensitive option names
    ini_parser.read(ini_path)

    try:
        section = ini_parser[section_to_search]
    except KeyError:
        return None

    data_source_connections = []
    regex_pattern = compile(regex)
    for key in section:
        if regex_pattern.search(key):
            if provider == "GeoPackage":  # TODO move this logic/condition into the rules if possible?
                source_name_raw = search(GPKG_SERVICE_NAME_REGEX, key)
                source_name = source_name_raw.group(0).replace("\\GPKG\\connections\\", "").replace("\\", "")
            else:
                source_name_raw = search(SERVICE_NAME_REGEX, key)
                source_name = source_name_raw.group(0).replace("\\", "")
            # TODO what are the replacements needed for?!

            # TODO "Bing VirtualEarth 💩" is not rendered well, also fails to import to other profile...
            source_name = unquote(source_name, 'latin-1')  # needed for e.g. %20 in connection names
            data_source_connections.append(source_name)

    return data_source_connections
