from configparser import RawConfigParser
from os import path
from shutil import copy2


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
        self.parser = RawConfigParser()
        self.parser.optionxform = str  # str = case sensitive option names

    def import_customizations(self):
        if path.exists(self.path_source_customini):
            copy2(self.path_source_customini, self.path_target_customini)

        ini_paths = self.profile_manager.get_ini_paths()

        self.parser.read(ini_paths["source"])

        if self.parser.has_section('UI'):
            ui_data = dict(self.parser.items('UI'))
            self.parser.clear()
            self.parser.read(ini_paths["target"])

            for setting in ui_data:
                if not self.parser.has_section("UI"):
                    self.parser["UI"] = {}

                self.parser.set("UI", setting, ui_data[setting])

            with open(ini_paths["target"], 'w') as qgisconf:
                self.parser.write(qgisconf, space_around_delimiters=False)

    def set_path_files(self, source, target):
        self.path_source_customini = self.profile_manager.adjust_to_operating_system(
            source + "QGIS/QGISCUSTOMIZATION3.ini"
        )
        self.path_target_customini = self.profile_manager.adjust_to_operating_system(
            target + "QGIS/QGISCUSTOMIZATION3.ini"
        )
