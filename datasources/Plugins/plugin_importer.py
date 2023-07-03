from configparser import RawConfigParser
from os import path
from pathlib import Path
from shutil import copytree

from qgis.PyQt.QtCore import Qt


class PluginImporter:

    def __init__(self, profile_manager):
        self.profile_manager = profile_manager
        self.parser = RawConfigParser()
        self.parser.optionxform = str  # str = case sensitive option names
        self.source_qgis_ini_file = ""
        self.target_qgis_ini_file = ""

    def import_selected_plugins(self):
        """Copies selected plugins into target profile.

        Copies the files and sets the INI options accordingly.
        Imported plugins are always set to be active.
        """
        self.parser.clear()
        self.parser.read(self.target_qgis_ini_file)

        if not self.parser.has_section("PythonPlugins"):
            self.parser["PythonPlugins"] = {}

        for item in self.profile_manager.dlg.list_plugins.findItems("", Qt.MatchContains | Qt.MatchRecursive):
            if item.checkState() == Qt.Checked:
                self.parser.set("PythonPlugins", item.text(), "true")

                profile_paths = self.profile_manager.get_profile_paths()

                source_plugins_dir = self.profile_manager.adjust_to_operating_system(
                    profile_paths["source"] + 'python/plugins/' + item.text() + '/')
                target_plugins_dir = self.profile_manager.adjust_to_operating_system(
                    profile_paths["target"] + 'python/plugins/' + item.text() + '/')

                if path.exists(source_plugins_dir):
                    if not path.exists(profile_paths["target"] + 'python/plugins/'):
                        Path(profile_paths["target"] + 'python/plugins/').mkdir(parents=True, exist_ok=True)
                    if not path.isdir(target_plugins_dir):
                        copytree(source_plugins_dir, target_plugins_dir)
                else:
                    continue

        with open(self.target_qgis_ini_file, 'w') as qgisconf:
            self.parser.write(qgisconf)

    def set_ini_paths(self, source, target):
        self.source_qgis_ini_file = source
        self.target_qgis_ini_file = target
