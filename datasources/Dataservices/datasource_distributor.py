# -*- coding: utf-8 -*-

from urllib.parse import quote
from configparser import RawConfigParser


class DatasourceDistributor:

    def __init__(self, profile_manager_dialog, profile_manager):
        self.dlg = profile_manager_dialog
        self.profile_manager = profile_manager
        self.parser = RawConfigParser()
        self.parser.optionxform = str
        self.dictionary_of_checked_database_sources = {}
        self.dictionary_of_checked_web_sources = {}
        self.dictionary_of_checked_sources = {}
        self.source_qgis_ini_file = ""
        self.target_qgis_ini_file = ""
        self.available_web_sources = {
            "WMS": [],
            "WFS": [],
            "WCS": [],
            "XYZ": [],
            "ArcGisMapServer": [],
            "ArcGisFeatureServer": [],
            "GeoNode": [],
        }

    def import_sources(self):
        """Handles data source import"""
        self.dictionary_of_checked_sources = {**self.dictionary_of_checked_database_sources,
                                              **self.dictionary_of_checked_web_sources}

        if self.dictionary_of_checked_sources:
            self.parser.clear()

            self.source_qgis_ini_file = self.profile_manager.adjust_to_operating_system(self.source_qgis_ini_file)
            self.target_qgis_ini_file = self.profile_manager.adjust_to_operating_system(self.target_qgis_ini_file)

            self.parser.read(self.source_qgis_ini_file)

            target_parser = RawConfigParser()
            target_parser.optionxform = str
            target_parser.read(self.target_qgis_ini_file)
            
            for key in self.dictionary_of_checked_sources:
                iterator = 0

                if key in self.available_web_sources:
                    if self.parser.has_section('qgis'):
                        for element in range(len(self.dictionary_of_checked_web_sources[key])):
                            self.import_web_sources(iterator, key, target_parser)
                            iterator += 1
                else:
                    for element in range(len(self.dictionary_of_checked_database_sources[key])):
                        self.import_db_sources(iterator, key, target_parser)
                        iterator += 1

            with open(self.target_qgis_ini_file, 'w') as qgisconf:
                target_parser.write(qgisconf)

        self.profile_manager.update_data_sources(False)

    def remove_sources(self):
        """Handles data source removal from file"""
        self.dictionary_of_checked_sources = {**self.dictionary_of_checked_database_sources,
                                              **self.dictionary_of_checked_web_sources}
                                              
        self.source_qgis_ini_file = self.profile_manager.adjust_to_operating_system(self.source_qgis_ini_file)
        self.target_qgis_ini_file = self.profile_manager.adjust_to_operating_system(self.target_qgis_ini_file)

        if self.dictionary_of_checked_sources:
            self.parser.clear()
            self.parser.read(self.source_qgis_ini_file)

            for key in self.dictionary_of_checked_sources:
                iterator = 0

                if key in self.available_web_sources:
                    if self.parser.has_section('qgis'):
                        for element in range(len(self.dictionary_of_checked_web_sources[key])):
                            self.remove_web_sources(key, iterator)
                            iterator += 1
                else:
                    for element in range(len(self.dictionary_of_checked_database_sources[key])):
                        self.remove_db_sources(key, iterator)
                        iterator += 1

                with open(self.source_qgis_ini_file, 'w') as qgisconf:
                    self.parser.write(qgisconf)

        self.profile_manager.update_data_sources(False)

    def import_web_sources(self, iterator, key, target_parser):
        """Imports web source strings to target file"""
        to_be_imported_dictionary_sources = dict(self.parser.items("qgis"))
        to_be_imported_dictionary_sources = dict(
            filter(lambda item: str("connections-" + key.lower()) in item[0],
                   to_be_imported_dictionary_sources.items()))
        to_be_imported_dictionary_sources = dict(
            filter(lambda item: "\\" + quote(
                self.dictionary_of_checked_web_sources[key][iterator].encode('latin-1')) + "\\" in item[
                                    0],
                   to_be_imported_dictionary_sources.items()))

        for data_source in to_be_imported_dictionary_sources:
            if not target_parser.has_section("qgis"):
                target_parser["qgis"] = {}
            target_parser.set("qgis", data_source, to_be_imported_dictionary_sources[data_source])

    def import_db_sources(self, iterator, key, target_parser):
        """Imports data base strings to target file"""
        to_be_imported_dictionary_sources = dict(self.parser.items(key))
        to_be_imported_dictionary_sources = dict(
            filter(lambda item: "\\" + quote(
                self.dictionary_of_checked_database_sources[key][iterator].encode('latin-1')) + "\\" in
                                item[0], to_be_imported_dictionary_sources.items()))
        for data_source in to_be_imported_dictionary_sources:
            if not target_parser.has_section(key):
                target_parser[key] = {}
            target_parser.set(key, data_source, to_be_imported_dictionary_sources[data_source])

    def remove_web_sources(self, key, iterator):
        """Removes web source strings from target file"""
        to_be_deleted_dictionary_sources = dict(self.parser.items("qgis"))
        to_be_deleted_dictionary_sources = dict(
            filter(lambda item: str("connections-" + key.lower()) in item[0],
                   to_be_deleted_dictionary_sources.items()))
        to_be_deleted_dictionary_sources = dict(
            filter(lambda item: "\\" + quote(
                self.dictionary_of_checked_web_sources[key][iterator].encode('latin-1')) + "\\" in item[0],
                   to_be_deleted_dictionary_sources.items()))

        for data_source in to_be_deleted_dictionary_sources:
            self.parser.remove_option("qgis", data_source)

    def remove_db_sources(self, key, iterator):
        """Remove data base sources from target file"""
        to_be_deleted_dictionary_sources = dict(self.parser.items(key))
        to_be_deleted_dictionary_sources = dict(
            filter(lambda item: "\\" + quote(
                self.dictionary_of_checked_database_sources[key][iterator].encode('latin-1')) + "\\" in
                                item[0], to_be_deleted_dictionary_sources.items()))

        for data_source in to_be_deleted_dictionary_sources:
            self.parser.remove_option(key, data_source)
