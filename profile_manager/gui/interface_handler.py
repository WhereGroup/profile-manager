from pathlib import Path

from qgis.core import Qgis, QgsApplication, QgsMessageLog
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QDialog

from profile_manager.datasources.dataservices.datasource_provider import (
    DATA_SOURCE_SEARCH_LOCATIONS,
    get_data_sources_tree,
)


class InterfaceHandler(QDialog):

    def __init__(self, profile_manager, profile_manager_dialog, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.profile_manager = profile_manager
        self.dlg = profile_manager_dialog
        self.checked = False

    def populate_data_source_tree(self, profile_name, populating_source_profile):
        """Populates the chosen profile's data source tree.

        Args:
            profile_name (str): Name of the profile for labelling
            populating_source_profile (bool): If the source profile is populated
        """
        QgsMessageLog.logMessage(
            f"Scanning profile '{profile_name}' for data source connections:",
            "Profile Manager",
            Qgis.Info,
        )
        ini_paths = self.profile_manager.get_ini_paths()
        if populating_source_profile:
            target_ini_path = ini_paths["source"]
        else:
            target_ini_path = ini_paths["target"]

        # collect data source tree items from ini file
        data_source_list = []
        for provider in DATA_SOURCE_SEARCH_LOCATIONS.keys():
            tree_root_item = get_data_sources_tree(
                target_ini_path, provider, make_checkable=populating_source_profile
            )
            if tree_root_item:
                data_source_list.append(tree_root_item)
        QgsMessageLog.logMessage(
            f"Scanning profile '{profile_name}' for data source connections: Done!",
            "Profile Manager",
            Qgis.Info,
        )

        # populate tree
        if populating_source_profile:
            self.dlg.treeWidgetSource.clear()
            self.dlg.treeWidgetSource.setHeaderLabel(
                self.tr("Source Profile: {}").format(profile_name)
            )
            for tree_root_item in data_source_list:
                self.dlg.treeWidgetSource.addTopLevelItem(tree_root_item)
        else:
            self.dlg.treeWidgetTarget.clear()
            self.dlg.treeWidgetTarget.setHeaderLabel(
                self.tr("Target Profile: {}").format(profile_name)
            )
            for tree_root_item in data_source_list:
                self.dlg.treeWidgetTarget.addTopLevelItem(tree_root_item)

    def populate_profile_listings(self):
        """Populates the main list as well as the comboboxes with available profile names.

        Also updates button states according to resulting selections.
        """
        self.dlg.comboBoxNamesSource.blockSignals(True)
        active_profile_name = Path(QgsApplication.qgisSettingsDirPath()).name

        self.dlg.comboBoxNamesSource.setCurrentText(active_profile_name)

        self.dlg.comboBoxNamesSource.blockSignals(False)
        self.dlg.comboBoxNamesTarget.blockSignals(False)
        self.dlg.list_profiles.blockSignals(False)
        self.conditionally_enable_profile_buttons()

    def setup_connections(self):
        """Set up connections"""
        # buttons
        self.dlg.importButton.clicked.connect(
            self.profile_manager.import_action_handler
        )
        self.dlg.closeDialog.rejected.connect(self.dlg.close)
        self.dlg.createProfileButton.clicked.connect(
            self.profile_manager.profile_manager_action_handler.create_new_profile
        )
        self.dlg.removeProfileButton.clicked.connect(
            self.profile_manager.profile_manager_action_handler.remove_profile
        )
        self.dlg.removeSourcesButton.clicked.connect(
            self.profile_manager.remove_source_action_handler
        )
        self.dlg.editProfileButton.clicked.connect(
            self.profile_manager.profile_manager_action_handler.edit_profile
        )
        self.dlg.copyProfileButton.clicked.connect(
            self.profile_manager.profile_manager_action_handler.copy_profile
        )

        # checkbox
        self.dlg.checkBox_checkAll.stateChanged.connect(self.check_everything)

        # selections/indexes
        self.dlg.comboBoxNamesSource.currentIndexChanged.connect(
            lambda: self.profile_manager.update_data_sources(False, True)
        )
        self.dlg.comboBoxNamesTarget.currentIndexChanged.connect(
            lambda: self.profile_manager.update_data_sources(True, False)
        )
        self.dlg.comboBoxNamesSource.currentIndexChanged.connect(
            self.conditionally_enable_import_button
        )
        self.dlg.comboBoxNamesTarget.currentIndexChanged.connect(
            self.conditionally_enable_import_button
        )
        self.dlg.list_profiles.selectionModel().selectionChanged.connect(
            self.conditionally_enable_profile_buttons
        )

    def check_everything(self):
        """Checks/Unchecks every checkbox in the gui"""
        if self.checked:
            self.uncheck_everything()
        else:
            for item in self.dlg.treeWidgetSource.findItems(
                "", Qt.MatchContains | Qt.MatchRecursive
            ):
                item.setCheckState(0, Qt.Checked)

            for item in self.dlg.list_plugins.findItems(
                "", Qt.MatchContains | Qt.MatchRecursive
            ):
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

        for item in self.dlg.treeWidgetSource.findItems(
            "", Qt.MatchContains | Qt.MatchRecursive
        ):
            item.setCheckState(0, Qt.Unchecked)

        for iterator in range(self.dlg.list_plugins.count()):
            self.dlg.list_plugins.item(iterator).setCheckState(Qt.Unchecked)

    def conditionally_enable_import_button(self):
        """Sets up buttons of the Import tab so that the user is not tempted to do "impossible" things.

        Called when profile selection changes in the Import tab.
        """

        # Don't allow import of a profile into itself
        if (
            self.dlg.comboBoxNamesSource.currentText()
            == self.dlg.comboBoxNamesTarget.currentText()
        ):
            self.dlg.importButton.setToolTip(
                self.tr("Target profile can not be same as source profile")
            )
            self.dlg.importButton.setEnabled(False)
        else:
            self.dlg.importButton.setToolTip("")
            self.dlg.importButton.setEnabled(True)

    def conditionally_enable_profile_buttons(self):
        """Sets up buttons of the Profiles tab so that the user is not tempted to do "impossible" things.

        Called when profile selection changes in the Profiles tab.
        """
        # A profile must be selected
        if self.dlg.get_list_selection_profile_name() is None:
            self.dlg.removeProfileButton.setToolTip(
                self.tr("Please choose a profile to remove")
            )
            self.dlg.removeProfileButton.setEnabled(False)
            self.dlg.editProfileButton.setToolTip(
                self.tr("Please choose a profile to rename")
            )
            self.dlg.editProfileButton.setEnabled(False)
            self.dlg.copyProfileButton.setToolTip(
                self.tr("Please select a profile to copy from")
            )
            self.dlg.copyProfileButton.setEnabled(False)
        # Some actions can/should not be done on the currently active profile
        elif (
            self.dlg.get_list_selection_profile_name()
            == Path(QgsApplication.qgisSettingsDirPath()).name
        ):
            self.dlg.removeProfileButton.setToolTip(
                self.tr("The active profile cannot be removed")
            )
            self.dlg.removeProfileButton.setEnabled(False)
            self.dlg.editProfileButton.setToolTip(
                self.tr("The active profile cannot be renamed")
            )
            self.dlg.editProfileButton.setEnabled(False)
            self.dlg.copyProfileButton.setToolTip("")
            self.dlg.copyProfileButton.setEnabled(True)
        else:
            self.dlg.removeProfileButton.setToolTip("")
            self.dlg.removeProfileButton.setEnabled(True)
            self.dlg.editProfileButton.setToolTip("")
            self.dlg.editProfileButton.setEnabled(True)
            self.dlg.copyProfileButton.setToolTip("")
            self.dlg.copyProfileButton.setEnabled(True)
