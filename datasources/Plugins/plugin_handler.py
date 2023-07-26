from qgis.PyQt.QtCore import Qt

from .plugin_displayer import PluginDisplayer
from .plugin_importer import import_plugins
from .plugin_remover import remove_plugins


class PluginHandler:

    def __init__(self, profile_manager):
        self.profile_manager = profile_manager
        self.plugin_displayer = PluginDisplayer(self.profile_manager)
        self.source_qgis_ini_file = ""
        self.target_qgis_ini_file = ""

    def populate_plugins_list(self, only_for_target_profile=False):
        """Gets active plugins from ini file and displays them in treeWidget"""
        self.set_path_files()
        self.plugin_displayer.set_ini_paths(self.source_qgis_ini_file, self.target_qgis_ini_file)
        self.plugin_displayer.populate_plugins_list(only_populate_target_profile=only_for_target_profile)

    def import_selected_plugins(self):
        """Import selected plugins into target profile"""
        source_profile_path, target_profile_path = self.profile_manager.get_profile_paths()

        plugin_names = []
        for item in self.profile_manager.dlg.list_plugins.findItems("", Qt.MatchContains | Qt.MatchRecursive):
            if item.checkState() == Qt.Checked:
                plugin_names.append(item.text())

        import_plugins(source_profile_path, target_profile_path, self.target_qgis_ini_file, plugin_names)
        self.populate_plugins_list()

    def remove_selected_plugins(self):
        """Removes selected plugins from source profile"""
        source_profile_path, _ = self.profile_manager.get_profile_paths()

        plugin_names = []
        for item in self.profile_manager.dlg.list_plugins.findItems("", Qt.MatchContains | Qt.MatchRecursive):
            if item.checkState() == Qt.Checked:
                plugin_names.append(item.text())

        remove_plugins(source_profile_path, self.source_qgis_ini_file, plugin_names)
        self.populate_plugins_list()

    def set_path_files(self):
        """Sets file paths"""
        ini_paths = self.profile_manager.get_ini_paths()
        self.source_qgis_ini_file = ini_paths["source"]
        self.target_qgis_ini_file = ini_paths["target"]
