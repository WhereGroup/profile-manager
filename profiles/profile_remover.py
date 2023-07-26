from pathlib import Path
from shutil import rmtree

from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.core import QgsApplication

from ..utils import adjust_to_operating_system, wait_cursor


class ProfileRemover(QDialog):

    def __init__(self, profile_manager_dialog, qgis_path, profile_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.dlg = profile_manager_dialog
        self.profile_manager = profile_manager
        self.qgis_path = qgis_path

    def remove_profile(self):
        """Removes profile

        Aborts and shows an error message if no backup could be made.
        """
        profile_item = self.dlg.list_profiles.currentItem()
        # bad states that should be prevented by the GUI
        assert profile_item is not None
        assert profile_item.text() != Path(QgsApplication.qgisSettingsDirPath()).name

        profile_name = profile_item.text()
        profile_path = adjust_to_operating_system(self.qgis_path + "/" + profile_name)

        clicked_button = QMessageBox.question(
            None,
            self.tr("Remove Profile"),
            self.tr("Are you sure you want to remove the profile '{0}'?\n\nA backup will be created at '{1}'") \
            .format(profile_name, self.profile_manager.backup_path),
        )

        if clicked_button == QMessageBox.Yes:
            error_message = None

            with wait_cursor():
                try:
                    self.profile_manager.make_backup(profile_name)
                except OSError as e:
                    error_message = \
                        self.tr("Aborting removal of profile '{0}' due to error:\n{1}").format(profile_name, e)
                if error_message:
                    QMessageBox.critical(None, self.tr("Backup could not be created"), error_message)
                    return

            with wait_cursor():
                try:
                    rmtree(profile_path)
                except FileNotFoundError as e:
                    error_message = self.tr("Aborting removal of profile '{0}' due to error:\n{1}") \
                        .format(profile_name, e)

            if error_message:
                QMessageBox.critical(
                    None, self.tr("Profile could not be removed"), error_message
                )
            else:
                QMessageBox.information(
                    None, self.tr("Profile removed"), self.tr("Profile '{}' has been removed.").format(profile_name)
                )
