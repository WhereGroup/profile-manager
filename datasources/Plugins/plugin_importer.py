# -*- coding: utf-8 -*-

from configparser import RawConfigParser
from pathlib import Path
from os import path
from shutil import copytree, rmtree
from PyQt5.QtCore import Qt


class PluginImporter:

    def __init__(self, profile_manager):
        self.profile_manager = profile_manager
        self.parser = RawConfigParser()
        self.parser.optionxform = str
        self.source_qgis_ini_file = ""
        self.target_qgis_ini_file = ""
        self.checked_items = []
        self.plugin_list_widget = self.profile_manager.dlg.list_plugins

    def import_active_plugins(self):
        """Copies plugin folders into target destination"""
        self.parser.clear()
        self.parser.read(self.target_qgis_ini_file)

        if not self.parser.has_section("PythonPlugins"):
            self.parser["PythonPlugins"] = {}

        self.plugin_list_widget = self.profile_manager.dlg.list_plugins
        for item in self.plugin_list_widget.findItems("", Qt.MatchContains | Qt.MatchRecursive):
            if item.checkState() == Qt.Checked:
                self.checked_items.append(item.text())
                self.parser.set("PythonPlugins", item.text(), "true")

                profile_paths = self.profile_manager.get_profile_paths()

                source_plugins_dir = self.profile_manager.adjust_to_operating_system(profile_paths["source"] + 'python/plugins/'
                                                                                     + item.text() + '/')
                target_plugins_dir = self.profile_manager.adjust_to_operating_system(profile_paths["target"] + 'python/plugins/'
                                                                                     + item.text() + '/')

                if path.exists(source_plugins_dir):
                    if not path.exists(profile_paths["target"] + 'python/plugins/'):
                        Path(profile_paths["target"] + 'python/plugins/').mkdir(parents=True, exist_ok=True)
                    if not path.isdir(target_plugins_dir):
                        copytree(source_plugins_dir, target_plugins_dir)
                else:
                    continue

        with open(self.target_qgis_ini_file, 'w') as qgisconf:
            self.parser.write(qgisconf)

        self.import_plugin_settings()

    def import_plugin_settings(self):
        """Gets plugin options from ini file and pastes them in target ini file"""
        self.parser.clear()
        self.parser.read(self.source_qgis_ini_file)

        for item in self.checked_items:
            get_plugin_options = []

            if not self.parser.has_section(item):
                continue
            else:
                get_plugin_options.append(self.parser.items(item))

            self.parser.clear()
            self.parser.read(self.target_qgis_ini_file)

            if not self.parser.has_section(item):
                self.parser[item] = {}

            for option in get_plugin_options[0]:
                self.parser.set(item, option[0], option[1])

            with open(self.target_qgis_ini_file, 'w') as qgisconf:
                self.parser.write(qgisconf)

    def set_ini_paths(self, source, target):
        self.source_qgis_ini_file = source
        self.target_qgis_ini_file = target
