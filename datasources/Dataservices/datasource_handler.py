from PyQt5.QtWidgets import QMessageBox
from .datasource_distributor import DatasourceDistributor
from ..Bookmarks.bookmark_handler import BookmarkHandler
from ..Customizations.customization_handler import CustomizationHandler
from ..Favourites.favourites_handler import FavouritesHandler
from ..Functions.function_handler import FunctionHandler
from ..Models.model_handler import ModelHandler
from ..Models.script_handler import ScriptHandler
from ..Plugins.plugin_handler import PluginHandler
from ..Styles.style_handler import StyleHandler
from ...utils import adjust_to_operating_system

class DataSourceHandler:

    def __init__(self, profile_manager_dialog, profile_manager):
        self.profile_manager = profile_manager
        self.dlg = profile_manager_dialog
        self.qgis_path = self.profile_manager.qgis_profiles_path
        self.dictionary_of_checked_web_sources = {}
        self.dictionary_of_checked_data_base_sources = {}
        self.source_profile_path = ""
        self.target_profile_path = ""
        self.source_qgis_ini_file = ""
        self.target_qgis_ini_file = ""
        self.source_bookmark_file = ""
        self.target_bookmark_file = ""
        self.datasource_distributor = DatasourceDistributor(self.profile_manager)
        self.plugin_handler = PluginHandler(self.profile_manager)
        self.bookmark_handler = BookmarkHandler()
        self.favourites_handler = FavouritesHandler()
        self.models_handler = ModelHandler()
        self.scripts_handler = ScriptHandler()
        self.styles_handler = StyleHandler()
        self.function_handler = FunctionHandler()
        self.customization_handler = CustomizationHandler(self.profile_manager)

    def set_data_sources(self, dictionary_of_checked_web_sources, dictionary_of_checked_data_base_sources):
        """Sets data sources"""
        self.dictionary_of_checked_web_sources = dictionary_of_checked_web_sources
        self.dictionary_of_checked_data_base_sources = dictionary_of_checked_data_base_sources

    def import_sources(self):
        """Handles the whole data import action.

        Returns:
            boolean: If errors were encountered.
        """
        had_errors = False

        self.setup_datasource_distributor()

        self.datasource_distributor.import_sources()

        if self.dlg.bookmark_check.isChecked():
            self.bookmark_handler.set_path_files(self.source_bookmark_file, self.target_bookmark_file)
            error_message = self.bookmark_handler.import_bookmarks()
            if error_message:
                had_errors = True
                QMessageBox.critical(None, "Error while importing bookmarks", error_message)

        if self.dlg.favourites_check.isChecked():
            self.favourites_handler.set_path_files(self.source_qgis_ini_file, self.target_qgis_ini_file)
            error_message = self.favourites_handler.import_favourites()
            if error_message:
                had_errors = True
                QMessageBox.critical(None, "Error while importing favourites", error_message)

        if self.dlg.models_check.isChecked():
            self.models_handler.set_path_files(self.source_profile_path + "processing/models/",
                                               self.target_profile_path + "processing/models/")
            self.models_handler.import_models()  # currently has no error handling

        if self.dlg.scripts_check.isChecked():
            self.scripts_handler.set_path_files(self.source_profile_path + "processing/scripts/",
                                                self.target_profile_path + "processing/scripts/")
            self.scripts_handler.import_scripts()  # currently has no error handling

        if self.dlg.styles_check.isChecked():
            self.styles_handler.set_db_connection(self.source_profile_path + "symbology-style.db",
                                                  self.target_profile_path + "symbology-style.db")
            error_message = self.styles_handler.import_styles()
            if error_message:
                had_errors = True
                QMessageBox.critical(None, "Error while importing styles", error_message)

        if self.dlg.functions_check.isChecked():
            self.function_handler.set_path_files(self.source_qgis_ini_file, self.target_qgis_ini_file)
            error_message = self.function_handler.import_functions()
            if error_message:
                had_errors = True
                QMessageBox.critical(None, "Error while importing expression functions", error_message)

        if self.dlg.ui_check.isChecked():
            self.customization_handler.set_path_files(self.source_profile_path, self.target_profile_path)
            self.customization_handler.import_customizations()  # currently has no error handling

        self.plugin_handler.import_selected_plugins()

        return had_errors

    def import_plugins(self):
        self.setup_datasource_distributor()
        self.plugin_handler.import_selected_plugins()

    def display_plugins(self, only_for_target_profile=False):
        """Displays plugins in treeWidget"""
        self.plugin_handler.set_path_files()
        self.plugin_handler.populate_plugins_list(only_for_target_profile=only_for_target_profile)

    def remove_sources(self):
        """Handles data removal"""
        self.setup_datasource_distributor()
        self.plugin_handler.remove_plugins()
        self.datasource_distributor.remove_sources()

    def set_path_to_files(self, source_profile_name, target_profile_name):
        """Sets file paths"""
        ini_paths = self.profile_manager.get_ini_paths()
        self.source_qgis_ini_file = ini_paths['source']
        self.target_qgis_ini_file = ini_paths['target']

        self.source_profile_path = adjust_to_operating_system(self.qgis_path + '/' + source_profile_name + '/')
        self.target_profile_path = adjust_to_operating_system(self.qgis_path + '/' + target_profile_name + '/')

    def set_path_to_bookmark_files(self, source_profile_name, target_profile_name):
        """Sets file paths"""
        self.source_bookmark_file = adjust_to_operating_system(
            self.qgis_path + '/' + source_profile_name + '/' + 'bookmarks.xml')
        self.target_bookmark_file = adjust_to_operating_system(
            self.qgis_path + '/' + target_profile_name + '/' + 'bookmarks.xml')

    def setup_datasource_distributor(self):
        """Sets up data source distributor"""
        self.datasource_distributor.dictionary_of_checked_web_sources = self.dictionary_of_checked_web_sources
        self.datasource_distributor.dictionary_of_checked_database_sources = \
            self.dictionary_of_checked_data_base_sources
        self.datasource_distributor.source_qgis_ini_file = self.source_qgis_ini_file
        self.datasource_distributor.target_qgis_ini_file = self.target_qgis_ini_file
