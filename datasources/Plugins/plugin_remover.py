# -*- coding: utf-8 -*-

from configparser import RawConfigParser
from os import path, chmod
from shutil import rmtree
from stat import S_IWRITE
from PyQt5.QtCore import Qt


class PluginRemover:

    def __init__(self, profile_manager):
        self.profile_manager = profile_manager
        self.parser = RawConfigParser()
        self.parser.optionxform = str
        self.source_qgis_ini_file = ""
        self.target_qgis_ini_file = ""
        self.checked_items = []
        self.plugin_list_widget = self.profile_manager.dlg.list_plugins

    def remove_plugins(self):
        """Copies plugin folders into target destination"""
        self.parser.clear()
        self.parser.read(self.source_qgis_ini_file)

        self.plugin_list_widget = self.profile_manager.dlg.list_plugins
        for item in self.plugin_list_widget.findItems("", Qt.MatchContains | Qt.MatchRecursive):
            if item.checkState() == Qt.Checked:
                self.checked_items.append(item.text())

                # Removes plugin from active state list in PythonPlugins Section
                if self.parser.has_option("PythonPlugins", item.text()):
                    self.parser.remove_option("PythonPlugins", item.text())

                profile_paths = self.profile_manager.get_profile_paths()

                source_plugins_dir = self.profile_manager.adjust_to_operating_system(profile_paths["source"] + 'python/plugins/'
                                                                                     + item.text() + '/')

                if path.exists(source_plugins_dir):
                    rmtree(source_plugins_dir, onerror=self.remove_readonly)
                else:
                    continue

        with open(self.source_qgis_ini_file, 'w') as qgisconf:
            self.parser.write(qgisconf)

    def set_ini_paths(self, source, target):
        self.source_qgis_ini_file = source
        self.target_qgis_ini_file = target

    def remove_readonly(self, func, path, excinfo):
        chmod(path, S_IWRITE)
        func(path)
