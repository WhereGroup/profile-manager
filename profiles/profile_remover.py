from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.core import QgsApplication
from pathlib import Path
from shutil import rmtree
from ..utils import wait_cursor


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

        profile_name = profile_item.text().replace(" - ", "")
        profile_path = self.profile_manager.adjust_to_operating_system(self.qgis_path + "/" + profile_name)

        clicked_button = QMessageBox.question(
            None,
            self.tr("Remove Profile!"),
            self.tr("Are you sure you want to delete the profile: ") + profile_name
            + "\n\nA backup will be created at " + self.profile_manager.backup_path,
        )

        if clicked_button == QMessageBox.Yes:
            with wait_cursor():
                try:
                    self.profile_manager.make_backup()
                except Exception as e:
                    QMessageBox.critical(
                        None,
                        self.tr("Backup could not be created"),
                        self.tr("Aborting removal of profile due to error:\n") + str(e),
                    )
                    return

                try:
                    rmtree(profile_path)
                except FileNotFoundError as e:
                    QMessageBox.critical(
                        None,
                        self.tr("Profile could not be removed"),
                        self.tr("Aborting due to error:\n") + str(e),
                    )
                    return

                QMessageBox.information(None, self.tr("Remove Profile"), self.tr("Profile has been removed!"))
