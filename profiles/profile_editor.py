from qgis.core import QgsApplication
from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from pathlib import Path
from os import rename
from ..utils import wait_cursor
from ..userInterface.name_profile_dialog import NameProfileDialog


class ProfileEditor(QDialog):

    def __init__(self, profile_manager_dialog, qgis_path, profile_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.dlg = profile_manager_dialog
        self.profile_manager = profile_manager
        self.qgis_path = qgis_path

    def edit_profile(self):
        """Renames profile with user input"""
        profile_item = self.dlg.list_profiles.currentItem()
        # bad states that should be prevented by the GUI
        assert profile_item is not None
        assert profile_item.text() != Path(QgsApplication.qgisSettingsDirPath()).name

        profile_before_change = self.profile_manager.adjust_to_operating_system(
            self.qgis_path + "/" + profile_item.text().replace(" - ", "")
        )

        dialog = NameProfileDialog(title=self.tr("Rename Profile!"))
        return_code = dialog.exec()

        if return_code == QDialog.Accepted:
            error_message = None
            with wait_cursor():
                profile_name = dialog.text_input.text()
                assert profile_name != ""  # should be forced by the GUI
                profile_after_change = self.profile_manager.adjust_to_operating_system(
                    self.qgis_path + "/" + profile_name
                )

                try:
                    rename(profile_before_change, profile_after_change)
                except IsADirectoryError as e:  # subclass of OSError
                    error_message = self.tr("Source is a file but destination is a directory.")
                except NotADirectoryError as e:  # subclass of OSError
                    error_message = self.tr("Source is a directory but destination is a file.")
                except PermissionError as e:  # subclass of OSError
                    error_message = self.tr("Operation not permitted.")
                except OSError as e:
                    # For other errors, e.g. target directory is not empty
                    error_message = str(e)

            if error_message:
                QMessageBox.critical(None, self.tr("Profile could not be renamed"), error_message)
            else:
                QMessageBox.information(
                    None,
                    self.tr("Profile renamed"),
                    self.tr("Source path renamed to destination path successfully."),
                )
