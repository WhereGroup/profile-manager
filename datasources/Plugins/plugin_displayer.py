from configparser import NoSectionError, RawConfigParser

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QListWidgetItem


class PluginDisplayer:

    def __init__(self, profile_manager):
        self.profile_manager = profile_manager
        self.parser = RawConfigParser()
        self.parser.optionxform = str
        self.parser_target = RawConfigParser()
        self.parser_target.optionxform = str
        self.source_qgis_ini_file = ""
        self.target_qgis_ini_file = ""
        self.checked_items = []
        self.active_plugins_from_profile = []
        self.core_plugins = [
            "GdalTools",
            "MetaSearch",
            "db_manager",
            "processing",
            "grassprovider",  # plugin since 3.22
        ]
        self.plugin_list_widget = self.profile_manager.dlg.list_plugins

    def show_active_plugins_in_list(self, only_populate_target_profile=False):
        """Gets active plugins from ini file and displays them in treeWidget

        Args:
            only_populate_target_profile (bool): If only the target list should be populated
        """
        self.parser.clear()

        if only_populate_target_profile:
            self.parser.read(self.target_qgis_ini_file)
            self.plugin_list_widget = self.profile_manager.dlg.list_plugins_target
        else:
            self.parser.read(self.source_qgis_ini_file)
            self.plugin_list_widget = self.profile_manager.dlg.list_plugins

        self.plugin_list_widget.clear()

        try:
            available_plugins_from_source_profile = dict(self.parser.items("PythonPlugins"))
        except NoSectionError:
            self.parser["PythonPlugins"] = {}
            available_plugins_from_source_profile = dict(self.parser.items("PythonPlugins"))

        active_plugins_from_source_profile = []

        for entry in available_plugins_from_source_profile:
            if entry in self.core_plugins:
                continue
            else:
                if available_plugins_from_source_profile[entry] == "true":
                    active_plugins_from_source_profile.append(entry)

                    list_entry = QListWidgetItem()
                    list_entry.setText(str(entry))
                    if not only_populate_target_profile:
                        list_entry.setFlags(list_entry.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                        list_entry.setCheckState(Qt.Unchecked)
                    self.plugin_list_widget.addItem(list_entry)

        self.active_plugins_from_profile = active_plugins_from_source_profile

        if not only_populate_target_profile:
            self.show_active_plugins_in_list(only_populate_target_profile=True)

    def set_ini_paths(self, source, target):
        self.source_qgis_ini_file = source
        self.target_qgis_ini_file = target
