# -*- coding: utf-8 -*-

from .plugin_importer import PluginImporter
from .plugin_remover import PluginRemover
from .plugin_displayer import PluginDisplayer


class PluginHandler:

    def __init__(self, profile_manager):
        self.profile_manager = profile_manager
        self.plugin_importer = PluginImporter(self.profile_manager)
        self.plugin_remover = PluginRemover(self.profile_manager)
        self.plugin_displayer = PluginDisplayer(self.profile_manager)
        self.source_qgis_ini_file = ""
        self.target_qgis_ini_file = ""

    def show_active_plugins_in_list(self, target=False):
        """Gets active plugins from ini file and displays them in treeWidget"""
        self.set_path_files()
        self.plugin_displayer.set_ini_paths(self.source_qgis_ini_file, self.target_qgis_ini_file)
        self.plugin_displayer.show_active_plugins_in_list(target)

    def import_active_plugins(self):
        """Import chosen plugins into target profile"""
        self.set_path_files()
        self.plugin_importer.set_ini_paths(self.source_qgis_ini_file, self.target_qgis_ini_file)
        self.plugin_importer.import_active_plugins()
        self.show_active_plugins_in_list()

    def remove_plugins(self):
        """Removes chosen plugins from source profile"""
        self.set_path_files()
        self.plugin_remover.set_ini_paths(self.source_qgis_ini_file, self.target_qgis_ini_file)
        self.plugin_remover.remove_plugins()
        self.show_active_plugins_in_list()

    def set_path_files(self):
        """Sets file path's"""
        ini_paths = self.profile_manager.get_ini_paths()
        self.source_qgis_ini_file = ini_paths["source"]
        self.target_qgis_ini_file = ini_paths["target"]
