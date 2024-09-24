from os import rename
from pathlib import Path

from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.core import QgsApplication

from ..userInterface.name_profile_dialog import NameProfileDialog
from ..utils import adjust_to_operating_system, wait_cursor


class ProfileEditor(QDialog):

    def __init__(self, profile_manager_dialog, qgis_path, profile_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.dlg = profile_manager_dialog
        self.profile_manager = profile_manager
        self.qgis_path = qgis_path

    def edit_profile(self):
        """Renames profile with user input"""
        old_profile_name = self.dlg.list_profiles.currentItem().text()
        # bad states that should be prevented by the GUI
        assert old_profile_name is not None
        assert old_profile_name != Path(QgsApplication.qgisSettingsDirPath()).name

        profile_before_change = adjust_to_operating_system(self.qgis_path + "/" + old_profile_name)

        dialog = NameProfileDialog(title=self.tr("Rename Profile '{}'").format(old_profile_name))
        return_code = dialog.exec()

        if return_code == QDialog.Accepted:
            error_message = None
            with wait_cursor():
                new_profile_name = dialog.text_input.text()
                assert new_profile_name != ""  # should be forced by the GUI
                profile_after_change = adjust_to_operating_system(self.qgis_path + "/" + new_profile_name)

                try:
                    rename(profile_before_change, profile_after_change)
                except OSError as e:
                    error_message = str(e)

            if error_message:
                QMessageBox.critical(None, self.tr("Profile could not be renamed"), error_message)
            else:
                QMessageBox.information(
                    None,
                    self.tr("Profile renamed"),
                    self.tr("Profile '{0}' successfully renamed to '{1}'.").format(old_profile_name, new_profile_name),
                )
