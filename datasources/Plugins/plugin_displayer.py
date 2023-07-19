from configparser import NoSectionError, RawConfigParser

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QListWidgetItem


class PluginDisplayer:

    def __init__(self, profile_manager):
        self.profile_manager = profile_manager
        self.source_qgis_ini_file = ""
        self.target_qgis_ini_file = ""

        # Via QGIS/python/plugins/CMakeLists.txt
        self.core_plugins = [
            "db_manager",
            "GdalTools",  # not a plugin anymore since QGIS 3.0
            "grassprovider",  # plugin since 3.22
            "MetaSearch",
            "otbprovider",  # plugin since 3.22
            "processing",
            "sagaprovider",  # removed in 3.30
        ]

    def populate_plugins_list(self, only_populate_target_profile=False):
        """Gets plugins from ini file and add them to treeWidget using their directory name

        Args:
            only_populate_target_profile (bool): If only the target list should be populated
        """
        ini_parser = RawConfigParser()
        ini_parser.optionxform = str  # str = case-sensitive option names

        if only_populate_target_profile:
            ini_parser.read(self.target_qgis_ini_file)
            plugin_list_widget = self.profile_manager.dlg.list_plugins_target
        else:
            ini_parser.read(self.source_qgis_ini_file)
            plugin_list_widget = self.profile_manager.dlg.list_plugins

        plugin_list_widget.clear()

        try:
            plugins_in_profile = dict(ini_parser.items("PythonPlugins"))
        except NoSectionError:
            ini_parser["PythonPlugins"] = {}
            plugins_in_profile = dict(ini_parser.items("PythonPlugins"))

        # add an item to the list for each non-core plugin
        for plugin_name in plugins_in_profile:
            item = QListWidgetItem()

            if not only_populate_target_profile:
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
            else:
                item.setFlags(item.flags() & ~Qt.ItemIsSelectable)

            if plugin_name in self.core_plugins:
                item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
                plugin_name = f"{plugin_name} (Core Plugin)"

            item.setText(str(plugin_name))
            plugin_list_widget.addItem(item)

        if not only_populate_target_profile:
            self.populate_plugins_list(only_populate_target_profile=True)

    def set_ini_paths(self, source, target):
        self.source_qgis_ini_file = source
        self.target_qgis_ini_file = target
