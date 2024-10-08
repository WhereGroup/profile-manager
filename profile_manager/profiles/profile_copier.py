from shutil import copytree

from qgis.PyQt.QtWidgets import QDialog, QMessageBox

from profile_manager.gui.name_profile_dialog import NameProfileDialog
from profile_manager.utils import wait_cursor


class ProfileCopier(QDialog):

    def __init__(self, profile_manager_dialog, qgis_path, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.dlg = profile_manager_dialog
        self.qgis_path = qgis_path

    def copy_profile(self):
        source_profile = self.dlg.get_list_selection_profile_name()
        assert source_profile is not None  # should be forced by the GUI
        source_profile_path = self.qgis_path + "/" + source_profile + "/"

        dialog = NameProfileDialog()
        return_code = dialog.exec()
        if return_code == QDialog.Accepted:
            error_message = None
            with wait_cursor():
                profile_name = dialog.text_input.text()
                assert profile_name != ""  # should be forced by the GUI
                profile_path = self.qgis_path + "/" + profile_name + "/"
                try:
                    copytree(source_profile_path, profile_path)
                except FileExistsError:
                    error_message = self.tr(
                        "Profile directory '{}' already exists."
                    ).format(profile_name)
            if error_message:
                QMessageBox.critical(
                    None, self.tr("Profile could not be copied"), error_message
                )
            else:
                QMessageBox.information(
                    None,
                    self.tr("Profile copied"),
                    self.tr("Profile '{}' successfully copied.").format(profile_name),
                )
