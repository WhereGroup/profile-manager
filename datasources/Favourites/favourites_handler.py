# -*- coding: utf-8 -*-

from configparser import RawConfigParser
import sys



class FavouritesHandler:

    def __init__(self, profile_manager):
        self.profile_manager = profile_manager
        self.parser = RawConfigParser()
        self.parser.optionxform = str
        self.source_qgis_ini_file = None
        self.target_qgis_ini_file = None

    def import_favourites(self):
        """Gets favourite options from ini file and pastes them in target file"""
        self.parser.clear()
        self.parser.read(self.source_qgis_ini_file)

        try:
            get_favourites = dict(self.parser.items("browser"))

            favourites_to_be_imported = {}
            favourites_to_be_preserved = ""

            for entry in get_favourites:
                if entry == "favourites":
                    favourites_to_be_imported[entry] = get_favourites[entry]

            self.parser.clear()
            self.parser.read(self.target_qgis_ini_file)

            if not self.parser.has_section("browser"):
                self.parser["browser"] = {}
            elif self.parser.has_option("browser", "favourites"):
                favourites_to_be_preserved = self.parser.get("browser", "favourites")

            import_string = favourites_to_be_imported["favourites"].replace(favourites_to_be_preserved, "")

            self.parser.set("browser", "favourites", favourites_to_be_preserved + import_string)

            with open(self.target_qgis_ini_file, 'w') as qgisconf:
                self.parser.write(qgisconf)
        except:
            print("Oops!", sys.exc_info()[0], "occurred.")

        

    def set_path_files(self, source_qgis_ini_file, target_qgis_ini_file):
        """Sets file path's"""
        self.source_qgis_ini_file = source_qgis_ini_file
        self.target_qgis_ini_file = target_qgis_ini_file


