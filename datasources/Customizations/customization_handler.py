from configparser import RawConfigParser
from os import path
from shutil import copy2

from ...utils import adjust_to_operating_system

class CustomizationHandler:
    """Handler for importing UI customizations, as stored in QGIS/QGISCUSTOMIZATION3.ini .

    E.g.
    [Customization]
    Browser=true
    Browser\AFS=false
    ...
    """

    def __init__(self, profile_manager):
        self.profile_manager = profile_manager
        self.path_source_customini = ""
        self.path_target_customini = ""

    def import_customizations(self):
        if path.exists(self.path_source_customini):
            copy2(self.path_source_customini, self.path_target_customini)

        ini_paths = self.profile_manager.get_ini_paths()

        source_ini_parser = RawConfigParser()
        source_ini_parser.optionxform = str  # str = case-sensitive option names
        source_ini_parser.read(ini_paths["source"])

        if source_ini_parser.has_section('UI'):
            ui_data = dict(source_ini_parser.items('UI'))

            target_ini_parser = RawConfigParser()
            target_ini_parser.optionxform = str  # str = case-sensitive option names
            target_ini_parser.read(ini_paths["target"])

            for setting in ui_data:
                if not target_ini_parser.has_section("UI"):
                    target_ini_parser["UI"] = {}

                target_ini_parser.set("UI", setting, ui_data[setting])

            with open(ini_paths["target"], 'w') as qgisconf:
                target_ini_parser.write(qgisconf, space_around_delimiters=False)

    def set_path_files(self, source, target):
        self.path_source_customini = adjust_to_operating_system(source + "QGIS/QGISCUSTOMIZATION3.ini")
        self.path_target_customini = adjust_to_operating_system(target + "QGIS/QGISCUSTOMIZATION3.ini")
