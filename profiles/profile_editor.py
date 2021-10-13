# -*- coding: utf-8 -*-

from qgis.core import QgsApplication
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QDialog
from pathlib import Path
from os import rename
from ..utils import wait_cursor
from ..userInterface.create_profile_dialog import CreateProfileDialog
from ..userInterface.message_box_factory import MessageBoxFactory


class ProfileEditor(QDialog):

    def __init__(self, profile_manager_dialog, qgis_path, profile_manager, profile_handler,error_text, *args, **kwargs):
        super(ProfileEditor, self).__init__(*args, **kwargs)

        self.dlg = profile_manager_dialog
        self.profile_handler = profile_handler
        self.profile_manager = profile_manager
        self.message_box_factory = MessageBoxFactory(self.dlg)
        self.qgis_path = qgis_path
        self.error_text = error_text

    def edit_profile(self):
        """Renames profile with user input"""
        if self.dlg.list_profiles.currentItem() is None:
            self.message_box_factory.create_message_box(self.error_text, self.tr("Please choose a profile to rename first!"))
        elif self.dlg.list_profiles.currentItem().text() == Path(QgsApplication.qgisSettingsDirPath()).name:
            self.message_box_factory.create_message_box(self.error_text, self.tr("The active profile cannot be renamed!"))
        else:          
            profile_before_change = self.profile_manager.adjust_to_operating_system(self.qgis_path + "/"
                                                                                    + self.dlg
                                                                                    .list_profiles.currentItem().text().replace(" - ", ""))

            dialog = CreateProfileDialog(self.dlg, self.profile_handler, True)
            dialog.exec_()

            while not self.profile_handler.is_cancel_button_clicked and not self.profile_handler.is_ok_button_clicked:
                QCoreApplication.processEvents()

            if self.profile_handler.is_ok_button_clicked:
                with wait_cursor():
                    if dialog.text_input.text() is "":
                        self.message_box_factory.create_message_box(self.error_text, self.tr("Please enter a new profile name!"))
                    else:
                        profile_after_change = self.profile_manager.adjust_to_operating_system(self.qgis_path + "/"
                                                                                            + dialog.text_input.text())

                        try:
                            rename(profile_before_change, profile_after_change)
                            print("Source path renamed to destination path successfully.")

                            # If Source is a file
                        # but destination is a directory
                        except IsADirectoryError:
                            print("Source is a file but destination is a directory.")

                            # If source is a directory
                        # but destination is a file
                        except NotADirectoryError:
                            print("Source is a directory but destination is a file.")

                            # For permission related errors
                        except PermissionError:
                            print("Operation not permitted.")

                            # For other errors
                        except OSError as error:
                            print(error)
                            self.message_box_factory.create_message_box(self.error_text, self.tr("Profile Directory already exists!"))