"""
/***************************************************************************
 ProfileManager
                                 A QGIS plugin
 Makes creating profiles easy by giving you an UI to easly import settings from other profiles
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-03-17
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Stefan Giese & Dominik Szill / WhereGroup GmbH
        email                : stefan.giese@wheregroup.com / dominik.szill@wheregroup.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

# Import the code for the dialog
import time
from collections import defaultdict
from os import path
from pathlib import Path
from shutil import copytree

# PyQGIS
from qgis.core import Qgis, QgsMessageLog, QgsUserProfileManager
from qgis.PyQt.QtCore import (
    QCoreApplication,
    QLocale,
    QSettings,
    QSize,
    Qt,
    QTranslator,
)
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QWidget

# plugin
from profile_manager.datasources.dataservices.datasource_handler import (
    DataSourceHandler,
)
from profile_manager.gui.interface_handler import InterfaceHandler
from profile_manager.profile_manager_dialog import ProfileManagerDialog
from profile_manager.profiles.profile_action_handler import ProfileActionHandler
from profile_manager.profiles.utils import get_profile_qgis_ini_path, qgis_profiles_path
from profile_manager.utils import adjust_to_operating_system, wait_cursor


class ProfileManager:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Classwide vars
        self.is_cancel_button_clicked = False
        self.is_ok_button_clicked = False
        self.backup_path = ""
        self.qgis_profiles_path = ""
        self.ini_path = ""
        self.operating_system = ""
        self.qgs_profile_manager = (
            None  # TODO in QGIS 3.30 we could and should use iface.userProfileManager()
        )
        self.data_source_handler: DataSourceHandler = None
        self.profile_manager_action_handler: ProfileActionHandler = None
        self.interface_handler: InterfaceHandler = None
        self.dlg = None

        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = path.dirname(__file__)
        # initialize locale

        locale = QSettings().value("locale/userLocale", QLocale().name())[0:2]
        locale_path = path.join(
            self.plugin_dir, "i18n", "ProfileManager_{}.qm".format(locale)
        )

        if path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr("&Profile Manager")

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate("ProfileManager", message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
    ):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        self.add_action(
            path.join(path.dirname(__file__), "icon.png"),
            text=self.tr("Profile Manager"),
            callback=self.run,
            parent=self.iface.mainWindow(),
        )

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(self.tr("&Profile Manager"), action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Run method that performs all the real work"""
        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        with wait_cursor():
            if self.first_start:
                self.first_start = False
                self.dlg = ProfileManagerDialog(parent=self.iface.mainWindow())
                self.dlg.setFixedSize(self.dlg.size())
                self.dlg.list_profiles.setIconSize(QSize(15, 15))

                self.set_paths()

                self.qgs_profile_manager = QgsUserProfileManager(
                    self.qgis_profiles_path
                )
                self.data_source_handler = DataSourceHandler(self.dlg, self)
                self.profile_manager_action_handler = ProfileActionHandler(
                    self.dlg, self.qgis_profiles_path, self
                )
                self.interface_handler = InterfaceHandler(self, self.dlg)

                self.interface_handler.setup_connections()

            self.interface_handler.populate_profile_listings()
            self.interface_handler.populate_data_source_tree(
                self.dlg.comboBoxNamesSource.currentText(), True
            )
            self.interface_handler.populate_data_source_tree(
                self.dlg.comboBoxNamesTarget.currentText(), False
            )

            self.data_source_handler.set_path_to_files(
                self.dlg.comboBoxNamesSource.currentText(),
                self.dlg.comboBoxNamesTarget.currentText(),
            )
            self.data_source_handler.display_plugins()

        self.dlg.exec()

    def set_paths(self):
        """Sets various OS and profile dependent paths"""
        self.qgis_profiles_path = str(qgis_profiles_path())

        self.backup_path = adjust_to_operating_system(
            str(Path.home()) + "/QGIS Profile Manager Backup/"
        )

    def make_backup(self, profile: str):
        """Creates a backup of the specified profile.

        Args:
            profile (str): Name of the profile to back up

        Raises:
            OSError: If copytree raises something
        """
        ts = int(time.time())
        target_path = self.backup_path + str(ts)
        source_path = f"{self.qgis_profiles_path}/{profile}"
        QgsMessageLog.logMessage(
            f"Backing up profile '{source_path}' to '{target_path}'",
            "Profile Manager",
            level=Qgis.Info,
        )
        copytree(source_path, target_path)

    def import_action_handler(self):
        """Handles data source import

        Aborts and shows an error message if no backup could be made.
        """
        error_message = None
        with wait_cursor():
            self.get_checked_sources()
            source_profile_name = self.dlg.comboBoxNamesSource.currentText()
            target_profile_name = self.dlg.comboBoxNamesTarget.currentText()
            assert (
                source_profile_name != target_profile_name
            )  # should be forced by the GUI
            self.data_source_handler.set_path_to_files(
                source_profile_name, target_profile_name
            )
            self.data_source_handler.set_path_to_bookmark_files(
                source_profile_name, target_profile_name
            )
            try:
                self.make_backup(target_profile_name)
            except OSError as e:
                error_message = self.tr("Aborting import due to error:\n{}").format(e)

            if error_message:
                QMessageBox.critical(
                    None, self.tr("Backup could not be created"), error_message
                )
                return

        with wait_cursor():
            self.data_source_handler.import_plugins()
            errors_on_sources = self.data_source_handler.import_all_the_things()
            self.update_data_sources(only_update_plugins_for_target_profile=True)

        if errors_on_sources:
            QMessageBox.critical(
                None,
                self.tr("Data Source Import"),
                self.tr(
                    "There were errors on import."
                ),  # The user should have been shown dialogs or see a log
            )
        else:
            QMessageBox.information(
                None,
                self.tr("Data Source Import"),
                self.tr(
                    "Data sources have been successfully imported.\n\n"
                    "Please refresh the QGIS Browser to see the changes."
                ),
            )
        self.interface_handler.uncheck_everything()
        self.refresh_browser_model()

    def remove_source_action_handler(self):
        """Handles data source removal

        Aborts and shows an error message if no backup could be made.
        """
        self.get_checked_sources()
        source_profile_name = self.dlg.comboBoxNamesSource.currentText()
        self.data_source_handler.set_path_to_files(source_profile_name, "")

        clicked_button = QMessageBox.question(
            None,
            self.tr("Remove Data Sources"),
            self.tr(
                "Are you sure you want to remove these sources?\n\nA backup will be created at '{}'"
            ).format(self.backup_path),
        )

        if clicked_button == QMessageBox.Yes:
            error_message = None
            with wait_cursor():
                try:
                    self.make_backup(source_profile_name)
                except OSError as e:
                    error_message = self.tr(
                        "Aborting removal due to error:\n{}"
                    ).format(e)

                if not error_message:
                    self.data_source_handler.remove_datasources_and_plugins()
                    self.update_data_sources(True)

            if error_message:
                QMessageBox.critical(
                    None, self.tr("Backup could not be created"), error_message
                )
            else:
                QMessageBox.information(
                    None,
                    self.tr("Data Sources Removed"),
                    self.tr(
                        "Data sources have been successfully removed.\n\n"
                        "Please refresh the QGIS Browser to see the changes."
                    ),
                )
                self.refresh_browser_model()
                self.interface_handler.uncheck_everything()

    def update_data_sources(
        self, only_update_plugins_for_target_profile=False, update_source=True
    ):
        """Updates data sources and plugin lists in the UI"""
        source_profile = self.dlg.comboBoxNamesSource.currentText()
        target_profile = self.dlg.comboBoxNamesTarget.currentText()

        if update_source:
            self.interface_handler.populate_data_source_tree(source_profile, True)
            self.interface_handler.populate_data_source_tree(target_profile, False)
        else:
            self.interface_handler.populate_data_source_tree(target_profile, False)

        self.data_source_handler.display_plugins(
            only_for_target_profile=only_update_plugins_for_target_profile
        )

    def get_checked_sources(self):
        """Gets all checked data sources and communicates them to the data source handler"""

        # TODO why is the split between web and db necessary??
        # TODO what titles does QGIS use in the GUI? can we use the same when needed in the plugin?

        checked_web_sources = defaultdict(list)
        checked_database_sources = defaultdict(list)

        for item in self.dlg.treeWidgetSource.findItems(
            "", Qt.MatchContains | Qt.MatchRecursive
        ):
            if item.childCount() == 0 and item.checkState(0) == Qt.Checked:
                parent_text = item.parent().text(0)  # the provider group in the tree
                item_text = item.text(
                    0
                )  # a specific data source in the provider's group
                # FIXME hardcoded list of GUI titles
                if parent_text in [
                    "SpatiaLite",
                    "PostgreSQL",
                    "MSSQL",
                    "DB2",
                    "Oracle",
                ]:
                    checked_database_sources[parent_text].append(item_text)
                # GeoPackage connections are stored under [providers] in the ini
                elif (
                    parent_text == "GeoPackage"
                ):  # FIXME hardcoded relationship between GeoPackage and 'providers'
                    checked_database_sources["providers"].append(item_text)
                else:
                    checked_web_sources[parent_text].append(item_text)

        self.data_source_handler.set_data_sources(
            checked_web_sources, checked_database_sources
        )

    def get_profile_paths(self) -> tuple[str, str]:
        """Returns the paths to the currently chosen source and target profiles.

        Returns:
            tuple[str, str]: Path to source profile, path to target profile
        """
        source = adjust_to_operating_system(
            self.qgis_profiles_path
            + "/"
            + self.dlg.comboBoxNamesSource.currentText()
            + "/"
        )
        target = adjust_to_operating_system(
            self.qgis_profiles_path
            + "/"
            + self.dlg.comboBoxNamesTarget.currentText()
            + "/"
        )

        return source, target

    def get_ini_paths(self):
        """Gets path to current chosen source and target qgis.ini file"""
        ini_paths = {
            "source": str(
                get_profile_qgis_ini_path(self.dlg.comboBoxNamesSource.currentText())
            ),
            "target": str(
                get_profile_qgis_ini_path(self.dlg.comboBoxNamesTarget.currentText())
            ),
        }

        return ini_paths

    def refresh_browser_model(self):
        """Refreshes the browser of the qgis instance from which this plugin was started"""
        self.iface.mainWindow().findChildren(QWidget, "Browser")[0].refresh()
        self.iface.mainWindow().findChildren(QWidget, "Browser2")[0].refresh()
