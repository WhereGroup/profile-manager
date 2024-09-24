from os import mkdir

from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.core import QgsUserProfileManager

from ..userInterface.name_profile_dialog import NameProfileDialog
from ..utils import adjust_to_operating_system, wait_cursor


class ProfileCreator(QDialog):

    def __init__(self, qgis_path, profile_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.profile_manager = profile_manager
        self.qgis_path = qgis_path
        self.qgs_profile_manager = QgsUserProfileManager(self.qgis_path)

    def create_new_profile(self):
        """Creates new profile with user inputs name"""
        dialog = NameProfileDialog()
        return_code = dialog.exec()
        if return_code == QDialog.Accepted:
            error_message = None
            with wait_cursor():
                profile_name = dialog.text_input.text()
                assert profile_name != ""  # should be forced by the GUI
                self.qgs_profile_manager.createUserProfile(profile_name)
                try:
                    if self.profile_manager.operating_system is "mac":
                        profile_path = self.qgis_path + "/" + profile_name + "/qgis.org/"
                    else:
                        profile_path = self.qgis_path + "/" + profile_name + "/QGIS/"

                    profile_path = adjust_to_operating_system(profile_path)
                    mkdir(profile_path)

                    ini_path = profile_path + adjust_to_operating_system('QGIS3.ini')
                    qgis_ini_file = open(ini_path, "w")
                    qgis_ini_file.close()
                except FileExistsError:
                    error_message = self.tr("Profile directory '{}' already exists.").format(profile_name)

            if error_message:
                QMessageBox.critical(None, self.tr("Profile could not be created"), error_message)
            else:
                QMessageBox.information(
                    None, self.tr("Profile created"), self.tr("Profile '{}' successfully created.").format(profile_name)
                )
