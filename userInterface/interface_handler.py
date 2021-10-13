from configparser import RawConfigParser
from qgis.PyQt.QtWidgets import QDialog, QListWidgetItem
from PyQt5.QtCore import Qt
from PyQt5 import QtGui


class InterfaceHandler(QDialog):

    def __init__(self, profile_manager, profile_manager_dialog, *args, **kwargs):
        super(InterfaceHandler, self).__init__(*args, **kwargs)

        self.profile_manager = profile_manager
        self.dlg = profile_manager_dialog
        self.data_source_provider = profile_manager.data_source_provider
        self.parser = RawConfigParser()
        self.parser.optionxform = str
        self.ini_path = ""
        self.checked = False

    def init_data_source_tree(self, profile_name, source_profile):
        """Initializes data sources"""
        ini_paths = self.profile_manager.get_ini_paths()

        if source_profile:
            self.ini_path = ini_paths["source"]
        else:
            self.ini_path = ini_paths["target"]

        self.parser.clear()
        self.parser.read(self.ini_path)
        self.data_source_provider.update_path(self.ini_path)

        data_source_list = [
            self.data_source_provider.get_data_base('^ogr.GPKG.connections.*path', "GeoPackage", "providers",
                                                    source_profile),
            self.data_source_provider.get_data_base('^connections.*sqlitepath', "SpatiaLite", "SpatiaLite",
                                                    source_profile),
            self.data_source_provider.get_data_base('^connections.*host', "PostgreSQL", "PostgreSQL", source_profile),
            self.data_source_provider.get_data_base('^connections.*host', "MSSQL", "MSSQL", source_profile),
            self.data_source_provider.get_data_base('^connections.*host', "DB2", "DB2", source_profile),
            self.data_source_provider.get_data_base('^connections.*host', "Oracle", "Oracle", source_profile),
            self.data_source_provider.get_data_sources('^connections-wms.*url', "WMS", source_profile),
            self.data_source_provider.get_data_sources('^connections-wfs.*url', "WFS", source_profile),
            self.data_source_provider.get_data_sources('^connections-wcs.*url', "WCS", source_profile),
            self.data_source_provider.get_data_sources('^connections-xyz.*url', "XYZ", source_profile),
            self.data_source_provider.get_data_sources('^connections-arcgismapserver.*url', "ArcGisMapServer",
                                                       source_profile),
            self.data_source_provider.get_data_sources('^connections-arcgisfeatureserver.*url', "ArcGisFeatureServer",
                                                       source_profile),
            self.data_source_provider.get_data_sources('^connections-geonode.*url', "GeoNode", source_profile)]

        self.display_datasources(source_profile, profile_name, data_source_list)

    def display_datasources(self, source_profile, profile_name, data_source_list):
        """Displays data source in the treeWidget"""
        # Display connections in the widgetTree
        if source_profile:
            self.dlg.treeWidgetSource.clear()
            self.dlg.treeWidgetSource.setHeaderLabel(self.tr("Source Profile: ") + profile_name)
            for dataSource in data_source_list:
                if dataSource is not None:
                    self.dlg.treeWidgetSource.addTopLevelItem(dataSource)
        else:
            self.dlg.treeWidgetTarget.clear()
            self.dlg.treeWidgetTarget.setHeaderLabel(self.tr("Target Profile: ") + profile_name)
            for dataSource in data_source_list:
                if dataSource is not None:
                    self.dlg.treeWidgetTarget.addTopLevelItem(dataSource)

    def init_profile_selection(self, profile="default"):
        """Gets the names of all existing profiles and displays them in a combobox"""
        profile_names = self.profile_manager.qgs_profile_manager.allProfiles()
        self.dlg.comboBoxNamesSource.clear()
        self.dlg.comboBoxNamesTarget.clear()
        self.dlg.list_profiles.clear()
        for name in profile_names:
            # Init source profiles combobox
            self.dlg.comboBoxNamesSource.addItem(name)
            self.dlg.comboBoxNamesSource.setCurrentIndex(profile_names.index(profile))
            # Init target profiles combobox
            self.dlg.comboBoxNamesTarget.addItem(name)
            # Add profiles to list view
            self.dlg.list_profiles.addItem(QListWidgetItem(QtGui.QIcon(':/plugins/profile_manager/icon.png'), name))

        self.dlg.comboBoxNamesSource.currentIndexChanged.connect(lambda: self.profile_manager.update_data_sources(False, True))
        self.dlg.comboBoxNamesTarget.currentIndexChanged.connect(lambda: self.profile_manager.update_data_sources(True, False))

    def adjust_to_macOSDark(self):
        from ..darkdetect import _detect
        if _detect.isDark():
            # Change ComboBox selected from black to white
            self.dlg.comboBoxNamesSource.setStyleSheet('color: white')
            self.dlg.comboBoxNamesTarget.setStyleSheet('color: white')

            # Set checkbox indicator of the treewidget from black to white
            file_tree_palette = QtGui.QPalette()
            file_tree_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(255, 255, 255))
            file_tree_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(30, 30, 30))
            file_tree_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(93, 93, 93))
            self.dlg.treeWidgetSource.setPalette(file_tree_palette)

            # set checkbox indiciator of listwidget from black to white
            self.dlg.list_plugins.setPalette(file_tree_palette)

    def init_ui_buttons(self):
        """Initializes all UI buttons"""
        self.dlg.importButton.clicked.connect(self.profile_manager.import_action_handler)
        self.dlg.closeDialog.rejected.connect(self.dlg.close)
        self.dlg.createProfileButton.clicked.connect(self.profile_manager.profile_manager_action_handler
                                                     .create_new_profile)
        self.dlg.removeProfileButton.clicked.connect(self.profile_manager.profile_manager_action_handler.remove_profile)
        self.dlg.removeSourcesButton.clicked.connect(self.profile_manager.remove_source_action_handler)
        self.dlg.editProfileButton.clicked.connect(self.profile_manager.profile_manager_action_handler.edit_profile)
        self.dlg.copyProfileButton.clicked.connect(self.profile_manager.profile_manager_action_handler.copy_profile)
    
        self.dlg.checkBox_checkAll.stateChanged.connect(self.check_everything)

    def check_everything(self):
        """Checks/Unchecks every checkbox in the gui"""
        if self.checked:
            self.uncheck_everything()
        else:
            for item in self.dlg.treeWidgetSource.findItems("", Qt.MatchContains | Qt.MatchRecursive):
                item.setCheckState(0, Qt.Checked)

            for item in self.dlg.list_plugins.findItems("", Qt.MatchContains | Qt.MatchRecursive):
                item.setCheckState(Qt.Checked)

            self.dlg.bookmark_check.setCheckState(Qt.Checked)
            self.dlg.favourites_check.setCheckState(Qt.Checked)
            self.dlg.models_check.setCheckState(Qt.Checked)
            self.dlg.scripts_check.setCheckState(Qt.Checked)
            self.dlg.styles_check.setCheckState(Qt.Checked)
            self.dlg.functions_check.setCheckState(Qt.Checked)
            self.dlg.ui_check.setChecked(Qt.Checked)

        self.checked = not self.checked

    def uncheck_everything(self):
        """Uncheck's every checkbox"""
        self.dlg.bookmark_check.setChecked(Qt.Unchecked)
        self.dlg.models_check.setChecked(Qt.Unchecked)
        self.dlg.favourites_check.setChecked(Qt.Unchecked)
        self.dlg.scripts_check.setChecked(Qt.Unchecked)
        self.dlg.styles_check.setChecked(Qt.Unchecked)
        self.dlg.functions_check.setChecked(Qt.Unchecked)
        self.dlg.ui_check.setChecked(Qt.Unchecked)
        self.dlg.checkBox_checkAll.setChecked(Qt.Unchecked)

        for item in self.dlg.treeWidgetSource.findItems("", Qt.MatchContains | Qt.MatchRecursive):
            item.setCheckState(0, Qt.Unchecked)

        for iterator in range(self.dlg.list_plugins.count()):
            self.dlg.list_plugins.item(iterator).setCheckState(Qt.Unchecked)

    def version_control(self):
        if self.profile_manager.get_qgis_version() < 3120:
            self.dlg.functions_check.setVisible(False)