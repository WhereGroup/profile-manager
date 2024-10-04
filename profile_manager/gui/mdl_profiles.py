from pathlib import Path

from qgis.core import QgsApplication, QgsUserProfile, QgsUserProfileManager
from qgis.PyQt.QtCore import QModelIndex, QObject, Qt
from qgis.PyQt.QtGui import QStandardItemModel

from profile_manager.profiles.utils import qgis_profiles_path


class ProfileListModel(QStandardItemModel):
    """QStandardItemModel to display available QGIS profile list"""

    NAME_COL = 0

    def __init__(self, parent: QObject = None):
        """
        QStandardItemModel for profile list display

        Args:
            parent: QObject parent
        """
        super().__init__(parent)
        self.setHorizontalHeaderLabels([self.tr("Name")])

        self.profile_manager = QgsUserProfileManager(str(qgis_profiles_path()))

        # Connect to profile changes
        self.profile_manager.setNewProfileNotificationEnabled(True)
        self.profile_manager.profilesChanged.connect(self._update_available_profiles)

        # Initialization of available profiles
        self._update_available_profiles()

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Define flags for an index.
        Used to disable edition.

        Args:
            index (QModelIndex): data index

        Returns:
            Qt.ItemFlags: flags
        """
        default_flags = super().flags(index)
        return default_flags & ~Qt.ItemIsEditable  # Disable editing

    def _update_available_profiles(self) -> None:
        """Update model with all available profiles in manager"""
        self.removeRows(0, self.rowCount())
        for profile_name in self.profile_manager.allProfiles():
            self.insert_profile(profile_name)

    def insert_profile(self, profile_name: str) -> None:
        """Insert profile in model

        Args:
            profile_name (str): profile name
        """
        # Get user profile
        profile: QgsUserProfile = self.profile_manager.profileForName(profile_name)
        if profile:
            row = self.rowCount()
            self.insertRow(row)
            self.setData(self.index(row, self.NAME_COL), profile.name())
            self.setData(
                self.index(row, self.NAME_COL), profile.icon(), Qt.DecorationRole
            )

            active_profile_folder_name = Path(QgsApplication.qgisSettingsDirPath()).name
            profile_folder_name = Path(profile.folder()).name
            if profile_folder_name == active_profile_folder_name:
                font = QgsApplication.font()
                font.setItalic(True)
                self.setData(self.index(row, self.NAME_COL), font, Qt.FontRole)
