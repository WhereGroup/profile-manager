# -*- coding: utf-8 -*-

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QDialog
from qgis.core import QgsApplication
from pathlib import Path
from os import rmdir
from shutil import rmtree
from ..utils import wait_cursor
from ..userInterface.remove_profile_dialog import RemoveProfileDialog
from ..userInterface.message_box_factory import MessageBoxFactory


class ProfileRemover(QDialog):

    def __init__(self, profile_manager_dialog, qgis_path, profile_manager, profile_handler, error_text, *args, **kwargs):
        super(ProfileRemover, self).__init__(*args, **kwargs)

        self.profile_handler = profile_handler
        self.dlg = profile_manager_dialog
        self.profile_manager = profile_manager
        self.message_box_factory = MessageBoxFactory(self.dlg)
        self.qgis_path = qgis_path
        self.error_text = error_text

    def remove_profile(self):
        """Removes profile"""
        if self.dlg.list_profiles.currentItem() is None:
            self.message_box_factory.create_message_box(self.error_text, self.tr("Please choose a profile to remove first!"))
        elif self.dlg.list_profiles.currentItem().text() == Path(QgsApplication.qgisSettingsDirPath()).name:
            self.message_box_factory.create_message_box(self.error_text, self.tr("The active profile cannot be deleted!"))
        else:
            profile_name = self.dlg.list_profiles.currentItem().text().replace(" - ", "")
            profile_path = self.profile_manager.adjust_to_operating_system(self.qgis_path + "/" + profile_name)

            dialog = RemoveProfileDialog(self.dlg, self.profile_handler, profile_name, self.profile_manager
                                        .adjust_to_operating_system(str(Path.home()) + "/QGISBackup/"), self.profile_manager)
            dialog.exec_()

            while not self.profile_handler.is_cancel_button_clicked and not self.profile_handler.is_ok_button_clicked:
                QCoreApplication.processEvents()

            if self.profile_handler.is_ok_button_clicked:
                with wait_cursor():
                    self.profile_manager.make_backup()
                    try:
                        rmtree(profile_path)
                        rmdir(profile_path)
                    except FileNotFoundError:
                        print('Error while deleting directory')

                    self.message_box_factory.create_message_box(self.tr("Remove Profile"), self.tr("Profile has been removed!"), "info")
