# -*- coding: utf-8 -*-

from ..Bookmarks.bookmark_handler import BookmarkHandler
from ..Favourites.favourites_handler import FavouritesHandler
from ..Plugins.plugin_handler import PluginHandler
from ..Models.model_handler import ModelHandler
from ..Models.script_handler import ScriptHandler
from ..Styles.style_handler import StyleHandler
from ..Functions.function_handler import FunctionHandler
from ..Customizations.customization_handler import CustomizationHandler
from .datasource_distributor import DatasourceDistributor


class DataSourceHandler:

    def __init__(self, profile_manager_dialog, profile_manager):
        self.profile_manager = profile_manager
        self.dlg = profile_manager_dialog
        self.qgis_path = self.profile_manager.qgis_path
        self.dictionary_of_checked_web_sources = {}
        self.dictionary_of_checked_data_base_sources = {}
        self.source_profile_path = ""
        self.target_profile_path = ""
        self.source_qgis_ini_file = ""
        self.target_qgis_ini_file = ""
        self.source_bookmark_file = ""
        self.target_bookmark_file = ""
        self.datasource_distributor = DatasourceDistributor(profile_manager_dialog, profile_manager)
        self.plugin_handler = PluginHandler(self.profile_manager)
        self.bookmark_handler = BookmarkHandler(self.qgis_path, self.profile_manager)
        self.favourites_handler = FavouritesHandler(self.profile_manager)
        self.models_handler = ModelHandler(self.profile_manager)
        self.scripts_handler = ScriptHandler(self.profile_manager)
        self.styles_handler = StyleHandler()
        self.function_handler = FunctionHandler(self.profile_manager)
        self.customization_handler = CustomizationHandler(self.profile_manager)

    def set_data_sources(self, dictionary_of_checked_web_sources, dictionary_of_checked_data_base_sources):
        """Sets data sources"""
        self.dictionary_of_checked_web_sources = dictionary_of_checked_web_sources
        self.dictionary_of_checked_data_base_sources = dictionary_of_checked_data_base_sources

        self.remove_empty_key_from_data_sources()

    def remove_empty_key_from_data_sources(self):
        """Removes empty keys from dict"""
        empty_keys_db_sources = [k for k, v in self.dictionary_of_checked_data_base_sources.items() if not v]
        for k in empty_keys_db_sources:
            del self.dictionary_of_checked_data_base_sources[k]

        empty_keys_web_sources = [k for k, v in self.dictionary_of_checked_web_sources.items() if not v]
        for k in empty_keys_web_sources:
            del self.dictionary_of_checked_web_sources[k]

    def import_sources(self):
        """Handles the whole data import action"""
        self.setup_datasource_distributor()

        self.datasource_distributor.import_sources()

        if self.dlg.bookmark_check.isChecked():
            self.bookmark_handler.set_path_files(self.source_bookmark_file, self.target_bookmark_file)
            self.bookmark_handler.parse_source_bookmarks()

        if self.dlg.favourites_check.isChecked():
            self.favourites_handler.set_path_files(self.source_qgis_ini_file, self.target_qgis_ini_file)
            self.favourites_handler.import_favourites()

        if self.dlg.models_check.isChecked():
            self.models_handler.set_path_files(self.source_profile_path + "processing/models/",
                                               self.target_profile_path + "processing/models/")
            self.models_handler.import_models()

        if self.dlg.scripts_check.isChecked():
            self.scripts_handler.set_path_files(self.source_profile_path + "processing/scripts/",
                                                self.target_profile_path + "processing/scripts/")
            self.scripts_handler.import_scripts()

        if self.dlg.styles_check.isChecked():
            self.styles_handler.set_db_connection(self.source_profile_path + "symbology-style.db",
                                                  self.target_profile_path + "symbology-style.db")
            self.styles_handler.import_styles()

        if self.profile_manager.get_qgis_version() >= 3120:
            if self.dlg.functions_check.isChecked():
                self.function_handler.set_path_files(self.source_qgis_ini_file, self.target_qgis_ini_file)
                self.function_handler.import_functions()
        
        if self.dlg.ui_check.isChecked():
            self.customization_handler.set_path_files(self.source_profile_path, self.target_profile_path)
            self.customization_handler.import_customizations()

        self.plugin_handler.import_active_plugins()

    def import_plugins(self):
        self.setup_datasource_distributor()
        self.plugin_handler.import_active_plugins()

    def display_plugins(self, update_plugins=False):
        """Displays plugins in treeWidget"""
        self.plugin_handler.set_path_files()
        self.plugin_handler.show_active_plugins_in_list(update_plugins)

    def remove_sources(self):
        """Handles data removal"""
        self.setup_datasource_distributor()
        self.plugin_handler.remove_plugins()
        self.datasource_distributor.remove_sources()

    def set_path_to_files(self, source_profile_name, target_profile_name):
        """Sets file path's"""
        ini_pathes = self.profile_manager.get_ini_paths()
        self.source_qgis_ini_file = ini_pathes['source']
        self.target_qgis_ini_file = ini_pathes['target']

        self.source_profile_path = self.profile_manager.adjust_to_operating_system(self.qgis_path + '/'
                                                                                   + source_profile_name + '/')
        self.target_profile_path = self.profile_manager.adjust_to_operating_system(self.qgis_path + '/'
                                                                                   + target_profile_name + '/')

    def set_path_to_bookmark_files(self, source_profile_name, target_profile_name):
        """Sets file path's"""
        self.source_bookmark_file = self.profile_manager.adjust_to_operating_system(
            self.qgis_path + '/' + source_profile_name + '/' + 'bookmarks.xml')
        self.target_bookmark_file = self.profile_manager.adjust_to_operating_system(
            self.qgis_path + '/' + target_profile_name + '/' + 'bookmarks.xml')

    def setup_datasource_distributor(self):
        """Sets up data source distributor"""
        self.datasource_distributor.dictionary_of_checked_web_sources = self.dictionary_of_checked_web_sources
        self.datasource_distributor\
            .dictionary_of_checked_database_sources = self.dictionary_of_checked_data_base_sources
        self.datasource_distributor.source_qgis_ini_file = self.source_qgis_ini_file
        self.datasource_distributor.target_qgis_ini_file = self.target_qgis_ini_file

