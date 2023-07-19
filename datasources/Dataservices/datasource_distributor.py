from configparser import RawConfigParser
from urllib.parse import quote

from ...utils import adjust_to_operating_system


class DatasourceDistributor:

    def __init__(self, profile_manager):
        self.profile_manager = profile_manager
        self.dictionary_of_checked_database_sources = {}
        self.dictionary_of_checked_web_sources = {}
        self.source_qgis_ini_file = ""
        self.target_qgis_ini_file = ""
        self.known_web_sources = [
            "Vector-Tile",
            "WMS",
            "WFS",
            "WCS",
            "XYZ",
            "ArcGisMapServer",
            "ArcGisFeatureServer",
            "GeoNode",
        ]  # must match the names in InterfaceHandler.populate_data_source_tree's data_source_list

    def import_sources(self):
        """Handles data source import"""
        dictionary_of_checked_sources = {**self.dictionary_of_checked_database_sources,
                                         **self.dictionary_of_checked_web_sources}

        if dictionary_of_checked_sources:
            self.source_qgis_ini_file = adjust_to_operating_system(self.source_qgis_ini_file)
            self.target_qgis_ini_file = adjust_to_operating_system(self.target_qgis_ini_file)

            source_ini_parser = RawConfigParser()
            source_ini_parser.optionxform = str  # str = case-sensitive option names
            source_ini_parser.read(self.source_qgis_ini_file)

            target_ini_parser = RawConfigParser()
            target_ini_parser.optionxform = str  # str = case-sensitive option names
            target_ini_parser.read(self.target_qgis_ini_file)

            for key in dictionary_of_checked_sources:
                iterator = 0

                if key in self.known_web_sources:
                    if source_ini_parser.has_section('qgis'):
                        for element in range(len(self.dictionary_of_checked_web_sources[key])):
                            self.import_web_sources(source_ini_parser, target_ini_parser, key, iterator)
                            iterator += 1
                else:
                    # seems to be a database source
                    for element in range(len(self.dictionary_of_checked_database_sources[key])):
                        self.import_db_sources(source_ini_parser, target_ini_parser, key, iterator)
                        iterator += 1

            with open(self.target_qgis_ini_file, 'w') as qgisconf:
                target_ini_parser.write(qgisconf, space_around_delimiters=False)

        self.profile_manager.update_data_sources(False)

    def remove_sources(self):
        """Handles data source removal from file"""
        dictionary_of_checked_sources = {**self.dictionary_of_checked_database_sources,
                                         **self.dictionary_of_checked_web_sources}

        self.source_qgis_ini_file = adjust_to_operating_system(self.source_qgis_ini_file)
        self.target_qgis_ini_file = adjust_to_operating_system(self.target_qgis_ini_file)

        if dictionary_of_checked_sources:
            parser = RawConfigParser()
            parser.optionxform = str  # str = case-sensitive option names
            parser.read(self.source_qgis_ini_file)

            for key in dictionary_of_checked_sources:
                iterator = 0

                if key in self.known_web_sources:
                    if parser.has_section('qgis'):
                        for element in range(len(self.dictionary_of_checked_web_sources[key])):
                            self.remove_web_sources(parser, key, iterator)
                            iterator += 1
                else:
                    # seems to be a database source
                    for element in range(len(self.dictionary_of_checked_database_sources[key])):
                        self.remove_db_sources(parser, key, iterator)
                        iterator += 1

                with open(self.source_qgis_ini_file, 'w') as qgisconf:
                    parser.write(qgisconf, space_around_delimiters=False)

        self.profile_manager.update_data_sources(False)

    def import_web_sources(
            self, source_ini_parser: RawConfigParser, target_ini_parser: RawConfigParser, key: str, iterator: int
    ):
        """Imports web source strings to target file"""

        # FIXME
        # The code below uses the user-visible titles of data source groups for looking up the corresponding lines
        # in the INI file. This obviously fails if we want to use nicely readable titles in the GUI.
        # The following replacement is a temporary workaround to allow this without too much of a refactor.
        # To be fixed when https://github.com/WhereGroup/profile-manager/issues/7 is solved.
        # get the whole qgis section
        to_be_imported_dictionary_sources = dict(source_ini_parser.items("qgis"))

        # filter to all entries matching the provider key (e. g. wms)
        to_be_imported_dictionary_sources = dict(
            filter(
                # FIXME store the key to lookup separately to allow different GUI display vs technical implementation
                lambda item: str("connections-" + key.lower()) in item[0], to_be_imported_dictionary_sources.items()
            )
        )

        # filter to all remaining entries matching the data source name
        to_be_imported_dictionary_sources = dict(
            filter(
                lambda item: "\\" + quote(
                    self.dictionary_of_checked_web_sources[key][iterator].encode('latin-1')
                ) + "\\" in item[0],
                to_be_imported_dictionary_sources.items()
            )
        )

        for data_source in to_be_imported_dictionary_sources:
            if not target_ini_parser.has_section("qgis"):
                target_ini_parser["qgis"] = {}
            target_ini_parser.set("qgis", data_source, to_be_imported_dictionary_sources[data_source])

    def import_db_sources(
            self, source_ini_parser: RawConfigParser, target_ini_parser: RawConfigParser, key: str, iterator: int
    ):
        """Imports data base strings to target file"""

        # filter to all entries matching the provider key (e. g. PostgreSQL)
        to_be_imported_dictionary_sources = dict(source_ini_parser.items(key))

        # filter to all remaining entries matching the data source name
        to_be_imported_dictionary_sources = dict(
            filter(
                lambda item: "\\" + quote(
                    self.dictionary_of_checked_database_sources[key][iterator].encode('latin-1')
                ) + "\\" in item[0],
                to_be_imported_dictionary_sources.items()
            )
        )

        for data_source in to_be_imported_dictionary_sources:
            if not target_ini_parser.has_section(key):
                target_ini_parser[key] = {}
            target_ini_parser.set(key, data_source, to_be_imported_dictionary_sources[data_source])

    def remove_web_sources(self, parser: RawConfigParser, key: str, iterator: int):
        """Removes web source strings from target file"""

        # get the whole qgis section
        to_be_deleted_dictionary_sources = dict(parser.items("qgis"))

        # filter to all entries matching the provider key (e. g. wms)
        to_be_deleted_dictionary_sources = dict(
            filter(
                lambda item: str("connections-" + key.lower()) in item[0],
                to_be_deleted_dictionary_sources.items()
            )
        )

        # filter to all remaining entries matching the data source name
        to_be_deleted_dictionary_sources = dict(
            filter(
                lambda item: "\\" + quote(
                    self.dictionary_of_checked_web_sources[key][iterator].encode('latin-1')
                ) + "\\" in item[0],
                to_be_deleted_dictionary_sources.items()
            )
        )

        for data_source in to_be_deleted_dictionary_sources:
            parser.remove_option("qgis", data_source)

    def remove_db_sources(self, parser: RawConfigParser, key: str, iterator: int):
        """Remove data base sources from target file"""

        # filter to all entries matching the provider key (e. g. PostgreSQL)
        to_be_deleted_dictionary_sources = dict(parser.items(key))

        # filter to all remaining entries matching the data source name
        to_be_deleted_dictionary_sources = dict(
            filter(
                lambda item: "\\" + quote(
                    self.dictionary_of_checked_database_sources[key][iterator].encode('latin-1')
                ) + "\\" in item[0],
                to_be_deleted_dictionary_sources.items()
            )
        )

        for data_source in to_be_deleted_dictionary_sources:
            parser.remove_option(key, data_source)
