from collections import defaultdict
from pathlib import Path
from typing import Optional, Literal

from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import QSize, Qt
from qgis.PyQt.QtWidgets import (
    QDialog,
    QListWidget,
    QMessageBox,
    QTreeWidget,
)

from qgis.core import QgsApplication

from profile_manager.gui.mdl_profiles import ProfileListModel
from profile_manager.gui.name_profile_dialog import NameProfileDialog
from profile_manager.gui.utils import (
    data_sources_as_tree,
    plugins_as_items,
)
from profile_manager.qdt_export.profile_export import (
    QDTProfileInfos,
    export_profile_for_qdt,
    get_qdt_profile_infos_from_file,
)
from profile_manager.utils import wait_cursor

FORM_CLASS, _ = uic.loadUiType(
    Path(__file__).parent.absolute() / "profile_manager_dialog_base.ui"
)


class ProfileManagerDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, profile_manager, parent=None):
        super().__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.__profile_manager = profile_manager
        self.__everything_is_checked = False

        self.profile_mdl = ProfileListModel(self)
        self.qdt_export_profile_cbx.setModel(self.profile_mdl)
        self.export_qdt_button.clicked.connect(self.export_qdt_handler)
        self.export_qdt_button.setEnabled(False)
        self.qdt_file_widget.fileChanged.connect(self._qdt_export_dir_changed)

        self.comboBoxNamesSource.setModel(self.profile_mdl)
        self.comboBoxNamesTarget.setModel(self.profile_mdl)
        self.list_profiles.setModel(self.profile_mdl)
        self.setFixedSize(self.size())
        self.list_profiles.setIconSize(QSize(15, 15))

        self.__setup_connections()

        # initial population of things on import tab
        self.comboBoxNamesSource.currentTextChanged.emit(
            self.comboBoxNamesSource.currentText()
        )
        self.comboBoxNamesTarget.currentTextChanged.emit(
            self.comboBoxNamesTarget.currentText()
        )

    def __setup_connections(self):
        """Set up connections"""
        # buttons
        self.importThingsButton.clicked.connect(self.__import_selected_things)
        self.removeThingsButton.clicked.connect(self.__remove_selected_things)

        self.createProfileButton.clicked.connect(self.__create_profile)
        self.removeProfileButton.clicked.connect(self.__remove_profile)
        self.editProfileButton.clicked.connect(self.__rename_profile)
        self.copyProfileButton.clicked.connect(self.__copy_profile)

        self.closeButton.rejected.connect(self.reject)

        # checkbox
        self.checkBox_checkAll.stateChanged.connect(self.__toggle_all_items)

        # selections/indexes
        self.comboBoxNamesSource.currentTextChanged.connect(
            self.__on_source_profile_changed
        )
        self.comboBoxNamesTarget.currentTextChanged.connect(
            self.__on_target_profile_changed
        )
        self.list_profiles.selectionModel().selectionChanged.connect(
            self.__conditionally_enable_profile_buttons
        )

    def get_list_selection_profile_name(self) -> Optional[str]:
        """Get selected profile name from list

        Returns:
            Optional[str]: selected profile name, None if no profile selected
        """
        index = self.list_profiles.selectionModel().currentIndex()
        if index.isValid():
            return self.list_profiles.model().data(index, ProfileListModel.NAME_COL)
        return None

    def _qdt_export_dir_changed(self) -> None:
        """Update UI when QDT export dir is changed:
        - enabled/disable button
        - define QDTProfileInformations if profile.json file is available
        """
        export_dir = self.qdt_file_widget.filePath()
        if export_dir:
            self.export_qdt_button.setEnabled(True)
            profile_json = Path(export_dir) / "profile.json"
            if profile_json.exists():
                self._set_qdt_profile_infos(
                    get_qdt_profile_infos_from_file(profile_json)
                )
        else:
            self.export_qdt_button.setEnabled(False)

    def _get_qdt_profile_infos(self) -> QDTProfileInfos:
        """Get QDTProfileInfos from UI

        Returns:
            QDTProfileInfos: QDT Profile Information
        """
        return QDTProfileInfos(
            description=self.qdt_description_edit.toPlainText(),
            email=self.qdt_email_edit.text(),
            version=self.qdt_version_edit.text(),
            qgis_min_version=self.qdt_qgis_min_version_edit.text(),
            qgis_max_version=self.qdt_qgis_max_version_edit.text(),
        )

    def _set_qdt_profile_infos(self, qdt_profile_infos: QDTProfileInfos) -> None:
        """Set QDTProfileInfos in UI

        Args:
            qdt_profile_infos (QDTProfileInfos): QDT Profile Information
        """
        self.qdt_description_edit.setPlainText(qdt_profile_infos.description)
        self.qdt_email_edit.setText(qdt_profile_infos.email)
        self.qdt_version_edit.setText(qdt_profile_infos.version)
        self.qdt_qgis_min_version_edit.setText(qdt_profile_infos.qgis_min_version)
        self.qdt_qgis_max_version_edit.setText(qdt_profile_infos.qgis_max_version)

    def export_qdt_handler(self) -> None:
        """Export selected profile as QDT profile"""
        profile_path = self.qdt_file_widget.filePath()
        if profile_path:
            source_profile_name = self.qdt_export_profile_cbx.currentText()
            export_profile_for_qdt(
                profile_name=source_profile_name,
                export_path=Path(profile_path),
                qdt_profile_infos=self._get_qdt_profile_infos(),
                clear_export_path=self.qdt_clear_export_folder_checkbox.isChecked(),
                export_inactive_plugin=self.qdt_inactive_plugin_export_checkbox.isChecked(),
            )
            QMessageBox.information(
                self,
                self.tr("QDT profile export"),
                self.tr("QDT profile have been successfully exported."),
            )

    def __conditionally_enable_import_buttons(self):
        source = self.__profile_manager.source_profile_name
        target = self.__profile_manager.target_profile_name
        if source == target:
            self.removeThingsButton.setEnabled(True)
            self.importThingsButton.setEnabled(False)
        elif source is None and target is not None:
            self.removeThingsButton.setEnabled(False)
            self.importThingsButton.setEnabled(False)
        elif source is not None and target is None:
            self.importThingsButton.setEnabled(False)
            self.removeThingsButton.setEnabled(True)
        else:
            self.importThingsButton.setEnabled(True)
            self.removeThingsButton.setEnabled(True)

    def __conditionally_enable_profile_buttons(self):
        """Sets up buttons of the Profiles tab so that the user is not tempted to do "impossible" things.

        Called when profile selection changes in the Profiles tab.
        """
        # A profile must be selected
        if self.get_list_selection_profile_name() is None:
            self.removeProfileButton.setToolTip(
                self.tr("Please choose a profile to remove")
            )
            self.removeProfileButton.setEnabled(False)
            self.editProfileButton.setToolTip(
                self.tr("Please choose a profile to rename")
            )
            self.editProfileButton.setEnabled(False)
            self.copyProfileButton.setToolTip(
                self.tr("Please select a profile to copy from")
            )
            self.copyProfileButton.setEnabled(False)
        # Some actions can/should not be done on the currently active profile
        elif (
            self.get_list_selection_profile_name()
            == Path(QgsApplication.qgisSettingsDirPath()).name
        ):
            self.removeProfileButton.setToolTip(
                self.tr("The active profile cannot be removed")
            )
            self.removeProfileButton.setEnabled(False)
            self.editProfileButton.setToolTip(
                self.tr("The active profile cannot be renamed")
            )
            self.editProfileButton.setEnabled(False)
            self.copyProfileButton.setToolTip("")
            self.copyProfileButton.setEnabled(True)
        else:
            self.removeProfileButton.setToolTip("")
            self.removeProfileButton.setEnabled(True)
            self.editProfileButton.setToolTip("")
            self.editProfileButton.setEnabled(True)
            self.copyProfileButton.setToolTip("")
            self.copyProfileButton.setEnabled(True)

    def __on_source_profile_changed(self, profile_name: str):
        self.__profile_manager.change_source_profile(profile_name)
        self.__conditionally_enable_import_buttons()

        if profile_name is None:
            self.treeWidgetSource.clear()
            self.list_plugins_source.clear()
        else:
            self.__update_data_sources_widget(
                "source", self.__profile_manager.source_data_sources
            )
            self.__update_plugins_widget(
                "source", self.__profile_manager.source_plugins
            )

    def __on_target_profile_changed(self, profile_name: str):
        self.__profile_manager.change_target_profile(profile_name)
        self.__conditionally_enable_import_buttons()

        if profile_name is None:
            self.treeWidgetTarget.clear()
            self.list_plugins_target.clear()
        else:
            self.__update_data_sources_widget(
                "target", self.__profile_manager.target_data_sources
            )
            self.__update_plugins_widget(
                "target", self.__profile_manager.target_plugins
            )

    def populate_profile_listings(self):
        """Populates the main list as well as the comboboxes with available profile names.

        Also updates button states according to resulting selections.

        TODO this docstring seems not correct anymore.
        TODO   how//where IS the profile model updated?
        TODO   document WHY blocksignals is used
        """
        self.comboBoxNamesSource.blockSignals(True)
        active_profile_name = Path(QgsApplication.qgisSettingsDirPath()).name
        self.comboBoxNamesSource.setCurrentText(active_profile_name)
        self.comboBoxNamesSource.blockSignals(False)

        self.__conditionally_enable_profile_buttons()

    def __populate_data_sources(
        self,
        data_sources: dict,
        data_sources_widget: QTreeWidget,
        make_checkable=True,
    ):
        """Populates the specified widget with a fancy list of available data sources.

        Args:
            data_sources: TODO
            data_sources_widget: The widget to populate
            make_checkable: If the data source items should be checkable by the user
        """
        # create tree items for discovered data sources, grouped by provider
        data_source_list = []
        for provider, provider_data_sources in data_sources.items():
            if not provider_data_sources:
                continue
            tree_root_item = data_sources_as_tree(
                provider, provider_data_sources, make_checkable=make_checkable
            )
            data_source_list.append(tree_root_item)

        # populate tree
        data_sources_widget.clear()
        for tree_root_item in data_source_list:
            data_sources_widget.addTopLevelItem(tree_root_item)

    def __populate_plugins_list(
        self, plugins: list[str], plugins_widget: QListWidget, make_checkable: bool
    ):
        """Populates the specified widget with a fancy list of available plugins.

        Args:
            plugins: Names of plugins
            plugins_widget: The widget to populate
            make_checkable: If the plugin items should be checkable by the user
        """
        items = plugins_as_items(plugins, make_checkable)

        plugins_widget.clear()
        for item in items:
            plugins_widget.addItem(item)

    def __set_checkstates(self, checkstate: Qt.CheckState):
        for item in self.treeWidgetSource.findItems(
            "", Qt.MatchFlag.MatchContains | Qt.MatchFlag.MatchRecursive
        ):
            item.setCheckState(0, checkstate)

        for item in self.list_plugins.findItems(
            "", Qt.MatchFlag.MatchContains | Qt.MatchFlag.MatchRecursive
        ):
            item.setCheckState(checkstate)

        self.bookmark_check.setCheckState(checkstate)
        self.favourites_check.setCheckState(checkstate)
        self.models_check.setCheckState(checkstate)
        self.scripts_check.setCheckState(checkstate)
        self.styles_check.setCheckState(checkstate)
        self.expressions_check.setCheckState(checkstate)
        self.checkBox_checkAll.setCheckState(checkstate)
        self.customization_check.setCheckState(checkstate)

    def __toggle_all_items(self):
        """Checks/Unchecks every checkbox in the gui"""
        if self.__everything_is_checked:
            checkstate = Qt.CheckState.Unchecked
        else:
            checkstate = Qt.CheckState.Checked
        self.__set_checkstates(checkstate)
        self.__everything_is_checked = not self.__everything_is_checked

    def __uncheck_everything(self):
        """Unchecks every checkbox"""
        self.__set_checkstates(Qt.CheckState.Unchecked)
        self.__everything_is_checked = False

    def __update_data_sources_widget(
        self, profile_to_update: Literal["source", "target"], data_sources: dict
    ):
        """Updates data sources and plugin lists in the UI"""
        if profile_to_update == "source":
            self.__populate_data_sources(
                data_sources=data_sources,
                data_sources_widget=self.treeWidgetSource,
                make_checkable=True,
            )
        elif profile_to_update == "target":
            self.__populate_data_sources(
                data_sources=data_sources,
                data_sources_widget=self.treeWidgetTarget,
                make_checkable=False,
            )
        else:
            raise ValueError("Only source or target profile can be updated")

    def __update_plugins_widget(
        self, profile_to_update: Literal["source", "target"], plugins: list[str]
    ):
        if profile_to_update == "source":
            self.__populate_plugins_list(
                plugins=plugins,
                plugins_widget=self.list_plugins,
                make_checkable=True,
            )
        elif profile_to_update == "target":
            self.__populate_plugins_list(
                plugins=plugins,
                plugins_widget=self.list_plugins_target,
                make_checkable=False,
            )
        else:
            raise ValueError("Only source or target profile can be updated")

    def __create_profile(self):
        """Creates a new profile"""
        name_dialog = NameProfileDialog()
        if name_dialog.exec() == QDialog.Rejected:
            return
        profile_name = name_dialog.text_input.text()

        with wait_cursor():
            error_message = self.__profile_manager.create_profile(profile_name)

        if error_message:
            QMessageBox.critical(
                self, self.tr("Profile could not be created"), error_message
            )
        else:
            QMessageBox.information(
                self,
                self.tr("Profile created"),
                self.tr("Profile '{}' successfully created.").format(profile_name),
            )

        self.populate_profile_listings()

    def __copy_profile(self):
        """Copies the selected profile"""
        source_profile_name = self.get_list_selection_profile_name()

        name_dialog = NameProfileDialog(
            title=self.tr("Name for copy of profile '{}'").format(source_profile_name)
        )
        if name_dialog.exec() == QDialog.Rejected:
            return
        target_profile_name = name_dialog.text_input.text()

        with wait_cursor():
            error_message = self.__profile_manager.copy_profile(
                source_profile_name, target_profile_name
            )

        if error_message:
            QMessageBox.critical(
                self,
                self.tr("Profile '{0}' could not be copied to '{1}'").format(
                    source_profile_name, target_profile_name
                ),
                error_message,
            )
        else:
            QMessageBox.information(
                self,
                self.tr("Profile copied"),
                self.tr("Profile '{0}' successfully copied to '{1}'.").format(
                    source_profile_name, target_profile_name
                ),
            )

        self.populate_profile_listings()

    def __rename_profile(self):
        """Renames the selected profile"""
        old_profile_name = self.get_list_selection_profile_name()

        name_dialog = NameProfileDialog()
        if name_dialog.exec() == QDialog.Rejected:
            return
        new_profile_name = name_dialog.text_input.text()

        with wait_cursor():
            error_message = self.__profile_manager.rename_profile(
                old_profile_name, new_profile_name
            )
        if error_message:
            QMessageBox.critical(
                self, self.tr("Profile could not be renamed"), error_message
            )
        else:
            QMessageBox.information(
                self,
                self.tr("Profile renamed"),
                self.tr("Profile '{0}' successfully renamed to '{1}'.").format(
                    old_profile_name, new_profile_name
                ),
            )

        self.populate_profile_listings()

    def __remove_profile(self):
        """Removes the selected profile (after creating a backup)."""
        profile_name = self.get_list_selection_profile_name()

        do_remove_profile = QMessageBox.question(
            self,
            self.tr("Remove Profile"),
            self.tr(
                "Are you sure you want to remove the profile '{0}'?\n\nA backup will be created at '{1}".format(
                    profile_name, self.__profile_manager.backup_path
                )
            ),
        )
        if do_remove_profile == QMessageBox.No:
            return

        with wait_cursor():
            error_message = self.__profile_manager.make_backup(profile_name)
        if error_message:
            QMessageBox.critical(
                self,
                self.tr("Backup could not be created"),
                self.tr("Aborting removal of profile '{0}' due to error:\n{1}").format(
                    profile_name, error_message
                ),
            )
            return

        with wait_cursor():
            error_message = self.__profile_manager.remove_profile(profile_name)
        if error_message:
            QMessageBox.critical(
                self, self.tr("Profile could not be removed"), error_message
            )
        else:
            QMessageBox.information(
                self,
                self.tr("Profile removed"),
                self.tr("Profile '{}' has been removed.").format(profile_name),
            )

        self.populate_profile_listings()

    def __selected_data_sources(self) -> dict[str, list[str]]:
        """Returns all data sources selected by the user in the source profile.

        Returns:
             provider -> [data source 1, data source 2, ...]
        """
        checked_data_sources = defaultdict(list)

        for item in self.treeWidgetSource.findItems(
            "", Qt.MatchFlag.MatchContains | Qt.MatchFlag.MatchRecursive
        ):
            if item.childCount() == 0 and item.checkState(0) == Qt.CheckState.Checked:
                # the provider group in the tree
                parent_text = item.parent().text(0)

                # a specific data source in the provider's group
                item_text = item.text(0)

                checked_data_sources[parent_text].append(item_text)

        return checked_data_sources

    def __selected_plugins(self) -> list[str]:
        """Returns all plugins (names) selected by the user in the source profile."""
        plugin_names = []
        for item in self.list_plugins.findItems(
            "", Qt.MatchFlag.MatchContains | Qt.MatchFlag.MatchRecursive
        ):
            if item.data(Qt.UserRole) is False:  # Core Plugins are marked with this
                continue
            if item.checkState() == Qt.CheckState.Checked:
                plugin_names.append(item.text())
        return plugin_names

    def __import_selected_things(self):
        """Import selected things from the source to the target profile.

        Aborts and shows an error message if no backup could be made.
        """

        with wait_cursor():
            error_message = self.__profile_manager.make_backup(
                self.__profile_manager.target_profile_name
            )
        if error_message:
            QMessageBox.critical(
                self,
                self.tr("Backup could not be created"),
                self.tr("Aborting import due to error:\n{}").format(error_message),
            )
            return

        with wait_cursor():
            selected_data_sources = self.__selected_data_sources()
            selected_plugins = self.__selected_plugins()
            error_messages = self.__profile_manager.import_things(
                data_sources=selected_data_sources,
                plugins=selected_plugins,
                do_import_bookmarks=self.bookmark_check.isChecked(),
                do_import_favourites=self.favourites_check.isChecked(),
                do_import_models=self.models_check.isChecked(),
                do_import_scripts=self.scripts_check.isChecked(),
                do_import_styles=self.styles_check.isChecked(),
                do_import_expressions=self.expressions_check.isChecked(),
                do_import_customizations=self.customization_check.isChecked(),
            )

        if error_messages:
            QMessageBox.critical(
                self, self.tr("Import Error(s)"), "\n".join(error_messages)
            )
        else:
            QMessageBox.information(
                self,
                self.tr("Import"),
                self.tr("Selected items have been successfully imported."),
            )

        with wait_cursor():
            if selected_data_sources:
                self.__update_data_sources_widget(
                    "target", self.__profile_manager.target_data_sources
                )
            if selected_plugins:
                self.__update_plugins_widget(
                    "target", self.__profile_manager.target_plugins
                )
            self.__uncheck_everything()

    def __remove_selected_things(self):
        """Removes selected things from the source profile.

        Aborts and shows an error message if no backup could be made.
        """

        do_remove_things = QMessageBox.question(
            self,
            self.tr("Removal"),
            self.tr(
                (
                    "Are you sure you want to remove the selected data sources and plugins?"
                    "\n\nA backup will be created at {}"
                )
            ).format(self.__profile_manager.backup_path),
        )
        if do_remove_things == QMessageBox.No:
            return

        with wait_cursor():
            error_message = self.__profile_manager.make_backup(
                self.__profile_manager.source_profile_name
            )
        if error_message:
            QMessageBox.critical(
                self,
                self.tr("Backup could not be created"),
                self.tr(
                    "Aborting removal of selected data sources and plugins due to error:\n{}"
                ).format(error_message),
            )
            return

        with wait_cursor():
            selected_data_sources = self.__selected_data_sources()
            selected_plugins = self.__selected_plugins()
            error_messages = self.__profile_manager.remove_things(
                data_sources=selected_data_sources, plugins=selected_plugins
            )
        if error_messages:
            QMessageBox.critical(
                self,
                self.tr("Removal Error(s)"),
                "\n".join(error_messages),
            )
        else:
            QMessageBox.information(
                self,
                self.tr("Removal"),
                self.tr(
                    "Selected data sources and plugins have been successfully removed."
                ),
            )

        with wait_cursor():
            if selected_data_sources:
                self.__update_data_sources_widget(
                    "source", self.__profile_manager.source_data_sources
                )
            if selected_plugins:
                self.__update_plugins_widget(
                    "source", self.__profile_manager.source_plugins
                )
        self.__uncheck_everything()
