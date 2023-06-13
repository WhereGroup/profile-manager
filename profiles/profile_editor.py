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
        if self.dlg.list_profiles.currentItem() is None:
            QMessageBox.critical(
                None, self.tr("Error"), self.tr("Please choose a profile to rename first!")
            )
        elif self.dlg.list_profiles.currentItem().text() == Path(QgsApplication.qgisSettingsDirPath()).name:
            QMessageBox.critical(
                None, self.tr("Error"), self.tr("The active profile cannot be renamed!")
            )
        else:
            profile_before_change = self.profile_manager.adjust_to_operating_system(
                self.qgis_path + "/" + self.dlg.list_profiles.currentItem().text().replace(" - ", "")
            )

            dialog = NameProfileDialog(title=self.tr("Rename Profile!"))
            return_code = dialog.exec()

            if return_code == QDialog.Accepted:
                with wait_cursor():
                    profile_name = dialog.text_input.text()
                    if profile_name is "":
                        QMessageBox.critical(
                            None, self.tr("Error"), self.tr("Please enter a new profile name!")
                        )
                    else:
                        profile_after_change = self.profile_manager.adjust_to_operating_system(
                            self.qgis_path + "/" + profile_name
                        )

                        try:
                            rename(profile_before_change, profile_after_change)
                            QMessageBox.information(
                                None,
                                self.tr("Profile renamed"),
                                self.tr("Source path renamed to destination path successfully."),
                            )

                        # If source is a file but destination is a directory
                        except IsADirectoryError as e:  # subclass of OSError
                            QMessageBox.critical(
                                None,
                                self.tr("Profile could not be renamed"),
                                self.tr("Source is a file but destination is a directory."),
                            )

                        # If source is a directory but destination is a file
                        except NotADirectoryError as e:  # subclass of OSError
                            QMessageBox.critical(
                                None,
                                self.tr("Profile could not be renamed"),
                                self.tr("Source is a directory but destination is a file."),
                            )

                        # For permission related errors
                        except PermissionError as e:  # subclass of OSError
                            QMessageBox.critical(
                                None, self.tr("Profile could not be renamed"), self.tr("Operation not permitted.")
                            )

                        # For other errors
                        except OSError as e:
                            # e.g. target directory is not empty
                            QMessageBox.critical(None, self.tr("Profile could not be renamed"), str(e))
