import logging
import time
from pathlib import Path
from shutil import copytree
from typing import Optional

from qgis.core import Qgis, QgsMessageLog, QgsUserProfileManager
from qgis.PyQt.QtCore import (
    QCoreApplication,
    QLocale,
    QSettings,
    QTranslator,
)
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QWidget

from profile_manager.datasources.bookmarks import import_bookmarks
from profile_manager.datasources.customization import (
    import_customizations,
)
from profile_manager.datasources.data_sources import (
    collect_data_sources,
    import_data_sources,
    remove_data_sources,
)
from profile_manager.datasources.favourites import import_favourites
from profile_manager.datasources.expressions import (
    import_expressions,
)
from profile_manager.datasources.models import import_models
from profile_manager.datasources.scripts import import_scripts
from profile_manager.datasources.plugins import (
    collect_plugin_names,
    remove_plugins,
    import_plugins,
)
from profile_manager.datasources.styles import import_styles

from profile_manager.profile_manager_dialog import ProfileManagerDialog
from profile_manager.profiles.profile_handler import (
    create_profile,
    copy_profile,
    rename_profile,
    remove_profile,
)
from profile_manager.profiles.utils import get_profile_qgis_ini_path, qgis_profiles_path
from profile_manager.utils import wait_cursor


LOGGER = logging.getLogger("profile_manager")
logging.basicConfig(
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.DEBUG,
)


class ProfileManager:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        self.backup_path = Path.home() / "QGIS Profile Manager Backup"

        # TODO in QGIS 3.30 we could and should use iface.userProfileManager()
        self.qgs_profile_manager = None

        self.__dlg: Optional[ProfileManagerDialog] = None

        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.__plugin_dir = Path(__file__).parent.absolute()

        # initialize locale
        locale = QSettings().value("locale/userLocale", QLocale().name())[0:2]
        locale_path = self.__plugin_dir / "i18n" / "ProfileManager_{}.qm".format(locale)
        if locale_path.exists():
            self.__translator = QTranslator()
            self.__translator.load(str(locale_path))
            QCoreApplication.installTranslator(self.__translator)

        # Declare instance attributes
        self.action: Optional[QAction] = None
        self.menu = self.tr("&Profile Manager")

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

        self.source_profile_name: Optional[str] = None  # e.g. "My Profile
        self.source_profile_path: Optional[Path] = None  # e.g. ".../My Profile"
        self.source_qgis_ini_file: Optional[Path] = None  # e.g. ".../QGIS3.ini"
        self.source_data_sources: Optional[dict] = None
        self.source_plugins: Optional[list] = None

        self.target_profile_name: Optional[str] = None  # e.g. "My Other Profile
        self.target_profile_path: Optional[Path] = None  # e.g. ".../My Other Profile"
        self.target_qgis_ini_file: Optional[Path] = None  # e.g. ".../QGIS3.ini"
        self.target_data_sources: Optional[dict] = None
        self.target_plugins: Optional[list] = None

    def __refresh_qgis_browser_panels(self):
        """Refreshes the browser of the qgis instance from which this plugin was started"""
        self.iface.mainWindow().findChildren(QWidget, "Browser")[0].refresh()
        self.iface.mainWindow().findChildren(QWidget, "Browser2")[0].refresh()

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon = QIcon(str(self.__plugin_dir / "icon.png"))
        action = QAction(icon, self.tr("Profile Manager"), self.iface.mainWindow())
        action.triggered.connect(self.run)
        action.setEnabled(True)
        self.iface.addToolBarIcon(action)
        self.iface.addPluginToMenu(self.menu, action)
        self.action = action

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        self.iface.removePluginMenu(self.menu, self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        """Run method that performs all the real work"""
        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        with wait_cursor():
            if self.first_start:
                self.first_start = False
                self.__dlg = ProfileManagerDialog(
                    profile_manager=self, parent=self.iface.mainWindow()
                )
                self.qgs_profile_manager = QgsUserProfileManager(
                    str(qgis_profiles_path())
                )

            # on any start:
            self.__dlg.populate_profile_listings()
            # data sources and plugins are populated via signals

        self.__dlg.exec()

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        return QCoreApplication.translate("ProfileManager", message)

    def change_source_profile(self, profile_name: str):
        # TODO handle profile_name=None without any attempts of data collecting
        self.source_profile_name = profile_name
        self.source_profile_path = qgis_profiles_path() / profile_name
        self.source_qgis_ini_file = get_profile_qgis_ini_path(profile_name)
        self.source_data_sources = collect_data_sources(self.source_qgis_ini_file)
        self.source_plugins = collect_plugin_names(self.source_qgis_ini_file)

    def change_target_profile(self, profile_name: str):
        # TODO handle profile_name=None without any attempts of data collecting
        self.target_profile_name = profile_name
        self.target_profile_path = qgis_profiles_path() / profile_name
        self.target_qgis_ini_file = get_profile_qgis_ini_path(profile_name)
        self.target_data_sources = collect_data_sources(self.target_qgis_ini_file)
        self.target_plugins = collect_plugin_names(self.target_qgis_ini_file)

    def make_backup(self, profile_name: str) -> Optional[str]:
        """Creates a backup of the specified profile.

        Args:
            profile_name (str): Name of the profile to back up

        Returns:
            str: A message if an error occured.
        """
        ts = int(time.time())
        target_path = self.backup_path / str(ts)
        source_path = qgis_profiles_path() / profile_name
        QgsMessageLog.logMessage(
            f"Backing up profile {profile_name!r} to {target_path!r}",
            "Profile Manager",
            level=Qgis.MessageLevel.Info,
        )
        try:
            copytree(source_path, target_path)
        except Exception as e:
            return self.tr("Error while creating backup: {}").format(e)

    def create_profile(self, profile_name: str) -> Optional[str]:
        try:
            create_profile(profile_name)
        except Exception as e:
            return self.tr(
                "Creation of profile '{0}' failed due to error:\n{1}"
            ).format(profile_name, e)

    def copy_profile(
        self, source_profile_name: str, target_profile_name: str
    ) -> Optional[str]:
        try:
            copy_profile(source_profile_name, target_profile_name)
        except Exception as e:
            return self.tr(
                "Copying of profile '{0}' to '{1}' failed due to error:\n{2}"
            ).format(source_profile_name, target_profile_name, e)

    def rename_profile(
        self, old_profile_name: str, new_profile_name: str
    ) -> Optional[str]:
        try:
            rename_profile(old_profile_name, new_profile_name)
        except Exception as e:
            return self.tr(
                "Renaming of profile '{0}' failed due to error:\n{1}"
            ).format(old_profile_name, e)

    def remove_profile(self, profile_name: str) -> Optional[str]:
        try:
            remove_profile(profile_name)
        except Exception as e:
            return self.tr("Removal of profile '{0}' failed due to error:\n{1}").format(
                profile_name, e
            )

    def import_things(
        self,
        data_sources: dict[str, list[str]],
        plugins: list[str],
        do_import_bookmarks: bool,
        do_import_favourites: bool,
        do_import_models: bool,
        do_import_scripts: bool,
        do_import_styles: bool,
        do_import_expressions: bool,
        do_import_customizations: bool,
    ) -> list[str]:
        """Handles import of all things supported."""
        # safety catch, should be prevented by the GUI
        if self.source_profile_name == self.target_profile_name:
            return [self.tr("Cannot import things from profile into itself")]
        if not self.target_profile_name:
            return [self.tr("No target profile selected")]

        error_messages = []
        if data_sources:
            QgsMessageLog.logMessage(
                self.tr("Importing {} data sources...").format(
                    sum([len(v) for v in data_sources.values()])
                ),
                "Profile Manager",
                level=Qgis.MessageLevel.Info,
            )
            try:
                import_data_sources(
                    qgis_ini_file=self.target_qgis_ini_file,
                    data_sources_to_be_imported=data_sources,
                    available_data_sources=self.source_data_sources,
                )
            except Exception as e:
                error_messages.append(
                    self.tr("Error while importing data sources: {}").format(e)
                )
            self.target_data_sources = collect_data_sources(self.target_qgis_ini_file)

        if plugins:
            QgsMessageLog.logMessage(
                self.tr("Importing {} plugins...").format(len(plugins)),
                "Profile Manager",
                level=Qgis.MessageLevel.Info,
            )
            try:
                import_plugins(
                    self.source_profile_path,
                    self.target_profile_path,
                    self.target_qgis_ini_file,
                    plugins,
                )
            except Exception as e:
                error_messages.append(
                    self.tr("Error while importing plugins: {}").format(e)
                )
            self.target_plugins = collect_plugin_names(self.target_qgis_ini_file)

        if do_import_bookmarks:
            QgsMessageLog.logMessage(
                self.tr("Importing bookmarks..."),
                "Profile Manager",
                level=Qgis.MessageLevel.Info,
            )
            try:
                import_bookmarks(
                    self.source_profile_path / "bookmarks.xml",
                    self.target_profile_path / "bookmarks.xml",
                )
            except Exception as e:
                error_messages.append(
                    self.tr("Error while importing bookmarks: {}").format(e)
                )

        if do_import_favourites:
            QgsMessageLog.logMessage(
                self.tr("Importing favourites..."),
                "Profile Manager",
                level=Qgis.MessageLevel.Info,
            )
            try:
                import_favourites(self.source_qgis_ini_file, self.target_qgis_ini_file)
            except Exception as e:
                error_messages.append(
                    self.tr("Error while importing favourites: {}").format(e)
                )

        if do_import_models:
            QgsMessageLog.logMessage(
                self.tr("Importing models..."),
                "Profile Manager",
                level=Qgis.MessageLevel.Info,
            )
            try:
                import_models(self.source_profile_path, self.target_profile_path)
            except Exception as e:
                error_messages.append(
                    self.tr("Error while importing models: {}").format(e)
                )

        if do_import_scripts:
            QgsMessageLog.logMessage(
                self.tr("Importing scripts..."),
                "Profile Manager",
                level=Qgis.MessageLevel.Info,
            )
            try:
                import_scripts(self.source_profile_path, self.target_profile_path)
            except Exception as e:
                error_messages.append(
                    self.tr("Error while importing scripts: {}").format(e)
                )

        if do_import_styles:
            QgsMessageLog.logMessage(
                self.tr("Importing styles..."),
                "Profile Manager",
                level=Qgis.MessageLevel.Info,
            )
            try:
                import_styles(self.source_profile_path, self.target_profile_path)
            except Exception as e:
                error_messages.append(
                    self.tr("Error while importing styles: {}").format(e)
                )

        if do_import_expressions:
            QgsMessageLog.logMessage(
                self.tr("Importing expressions..."),
                "Profile Manager",
                level=Qgis.MessageLevel.Info,
            )
            try:
                import_expressions(self.source_qgis_ini_file, self.target_qgis_ini_file)
            except Exception as e:
                error_messages.append(
                    self.tr("Error while importing expressions: {}").format(e)
                )

        if do_import_customizations:
            QgsMessageLog.logMessage(
                self.tr("Importing customizations..."),
                "Profile Manager",
                level=Qgis.MessageLevel.Info,
            )
            try:
                import_customizations(
                    self.source_profile_path, self.target_profile_path
                )
            except Exception as e:
                error_messages.append(
                    self.tr("Error while importing UI customizations: {}").format(e)
                )

        self.__refresh_qgis_browser_panels()

    def remove_things(
        self, data_sources: dict[str, list[str]], plugins: list[str]
    ) -> list[str]:
        """Handles removal of data sources and plugins. Other things are not supported (yet)."""
        error_messages = []

        if data_sources:
            QgsMessageLog.logMessage(
                self.tr("Removing {} data sources...").format(
                    sum([len(v) for v in data_sources.values()])
                ),
                "Profile Manager",
                level=Qgis.MessageLevel.Info,
            )
            try:
                remove_data_sources(
                    qgis_ini_file=self.source_qgis_ini_file,
                    data_sources_to_be_removed=data_sources,
                    available_data_sources=self.source_data_sources,
                )
            except Exception as e:
                error_messages.append(
                    self.tr("Error while removing data sources: {}").format(e)
                )
            self.source_data_sources = collect_data_sources(self.source_qgis_ini_file)

        if plugins:
            QgsMessageLog.logMessage(
                self.tr("Removing {} plugins...").format(len(plugins)),
                "Profile Manager",
                level=Qgis.MessageLevel.Info,
            )
            try:
                remove_plugins(
                    self.source_profile_path,
                    self.source_qgis_ini_file,
                    plugins,
                )
            except Exception as e:
                error_messages.append(
                    self.tr("Error while removing plugins: {}").format(e)
                )
            self.source_plugins = collect_plugin_names(self.source_qgis_ini_file)

        self.__refresh_qgis_browser_panels()

        return error_messages
