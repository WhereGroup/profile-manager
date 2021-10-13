# -*- coding: utf-8 -*-

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QDialog
from qgis.core import QgsUserProfileManager
from ..utils import wait_cursor
from shutil import copytree
from ..userInterface.create_profile_dialog import CreateProfileDialog
from ..userInterface.message_box_factory import MessageBoxFactory


class ProfileCopier(QDialog):

    def __init__(self, profile_manager_dialog, qgis_path, profile_manager, profile_handler, error_text, *args, **kwargs):
        super(ProfileCopier, self).__init__(*args, **kwargs)

        self.dlg = profile_manager_dialog
        self.profile_handler = profile_handler
        self.profile_manager = profile_manager
        self.is_cancel_button_clicked = False
        self.is_ok_button_clicked = False
        self.message_box_factory = MessageBoxFactory(self.dlg)
        self.qgis_path = qgis_path
        self.qgs_profile_manager = QgsUserProfileManager(self.qgis_path)
        self.error_text = error_text

    def copy_profile(self):
        if self.dlg.list_profiles.currentItem():
            source_profile = self.dlg.list_profiles.currentItem()
            source_profile_path =self.qgis_path + "/" + source_profile.text().replace(" - ", "") + "/"
            dialog = CreateProfileDialog(self.dlg, self.profile_handler)
            dialog.exec_()

            while not self.profile_handler.is_cancel_button_clicked and not self.profile_handler.is_ok_button_clicked:
                QCoreApplication.processEvents()

            if self.profile_handler.is_ok_button_clicked:
                with wait_cursor():
                    new_profile = dialog.text_input.text()
                    if new_profile is "":
                        self.message_box_factory.create_message_box(self.error_text, self.tr("No profile name provided!"))
                    else:

                        profile_path = self.qgis_path + "/" + new_profile + "/"

                        try:
                            copytree(source_profile_path, profile_path)
                        except FileExistsError:
                            self.message_box_factory.create_message_box(self.error_text, self.tr("Profile Directory already exists!"))
        else:
            self.message_box_factory.create_message_box(self.error_text, self.tr("Please select a profile to copy from!"))