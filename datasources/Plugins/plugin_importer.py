from configparser import RawConfigParser
from os import path
from pathlib import Path
from shutil import copytree

from qgis.PyQt.QtCore import Qt

from ...utils import adjust_to_operating_system


class PluginImporter:

    def __init__(self, profile_manager):
        self.profile_manager = profile_manager
        self.source_qgis_ini_file = ""
        self.target_qgis_ini_file = ""

    def import_selected_plugins(self):
        """Copies selected plugins into target profile.

        Copies the files and sets the INI options accordingly.
        Imported plugins are always set to be active.
        """
        ini_parser = RawConfigParser()
        ini_parser.optionxform = str  # str = case-sensitive option names
        ini_parser.read(self.target_qgis_ini_file)

        if not ini_parser.has_section("PythonPlugins"):
            ini_parser["PythonPlugins"] = {}

        for item in self.profile_manager.dlg.list_plugins.findItems("", Qt.MatchContains | Qt.MatchRecursive):
            if item.checkState() == Qt.Checked:
                ini_parser.set("PythonPlugins", item.text(), "true")

                profile_paths = self.profile_manager.get_profile_paths()

                source_plugins_dir = adjust_to_operating_system(
                    profile_paths["source"] + 'python/plugins/' + item.text() + '/')
                target_plugins_dir = adjust_to_operating_system(
                    profile_paths["target"] + 'python/plugins/' + item.text() + '/')

                if path.exists(source_plugins_dir):
                    if not path.exists(profile_paths["target"] + 'python/plugins/'):
                        Path(profile_paths["target"] + 'python/plugins/').mkdir(parents=True, exist_ok=True)
                    if not path.isdir(target_plugins_dir):
                        copytree(source_plugins_dir, target_plugins_dir)
                else:
                    continue

        with open(self.target_qgis_ini_file, 'w') as qgisconf:
            ini_parser.write(qgisconf, space_around_delimiters=False)

    def set_ini_paths(self, source, target):
        self.source_qgis_ini_file = source
        self.target_qgis_ini_file = target
