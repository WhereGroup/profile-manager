from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from ..utils import wait_cursor
from shutil import copytree
from ..userInterface.name_profile_dialog import NameProfileDialog


class ProfileCopier(QDialog):

    def __init__(self, profile_manager_dialog, qgis_path, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.dlg = profile_manager_dialog
        self.qgis_path = qgis_path

    def copy_profile(self):
        if self.dlg.list_profiles.currentItem():
            source_profile = self.dlg.list_profiles.currentItem()
            source_profile_path = self.qgis_path + "/" + source_profile.text().replace(" - ", "") + "/"

            dialog = NameProfileDialog()
            return_code = dialog.exec()
            if return_code == QDialog.Accepted:
                with wait_cursor():
                    profile_name = dialog.text_input.text()
                    if profile_name is "":
                        QMessageBox.critical(None, self.tr("Error"), self.tr("No profile name provided!"))
                        return

                    profile_path = self.qgis_path + "/" + profile_name + "/"
                    try:
                        copytree(source_profile_path, profile_path)
                    except FileExistsError:
                        QMessageBox.critical(None, self.tr("Error"), self.tr("Profile Directory already exists!"))
        else:
            QMessageBox.critical(None, self.tr("Error"), self.tr("Please select a profile to copy from!"))
