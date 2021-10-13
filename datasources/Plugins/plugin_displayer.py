# -*- coding: utf-8 -*-

from configparser import RawConfigParser, NoSectionError
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt


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
        self.core_plugins = ["GdalTools", "MetaSearch", "db_manager", "processing"]
        self.plugin_list_widget = self.profile_manager.dlg.list_plugins

    def show_active_plugins_in_list(self, target=False):
        """Gets active plugins from ini file and displays them in treeWidget"""
        if target:
            self.show_active_plugins_in_target_list()
        else:        
            self.parser.clear()

            if target:
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

                        list_entry = QtWidgets.QListWidgetItem()
                        list_entry.setText(str(entry))
                        if not target:
                            list_entry.setFlags(list_entry.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                            list_entry.setCheckState(Qt.Unchecked)
                        self.plugin_list_widget.addItem(list_entry)

            self.active_plugins_from_profile = active_plugins_from_source_profile

            if not target:
                self.show_active_plugins_in_list(True)


    def show_active_plugins_in_target_list(self):
        """Gets active plugins from ini file and displays them in treeWidget"""
        self.parser.clear()

        self.parser.read(self.target_qgis_ini_file)
        self.plugin_list_widget = self.profile_manager.dlg.list_plugins_target

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

                    list_entry = QtWidgets.QListWidgetItem()
                    list_entry.setText(str(entry))
                    
                    self.plugin_list_widget.addItem(list_entry)

        self.active_plugins_from_profile = active_plugins_from_source_profile

    def set_ini_paths(self, source, target):
        self.source_qgis_ini_file = source
        self.target_qgis_ini_file = target
