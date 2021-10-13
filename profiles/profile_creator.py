# -*- coding: utf-8 -*-

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QDialog
from qgis.core import QgsUserProfileManager
from os import mkdir
from ..utils import wait_cursor
from ..userInterface.create_profile_dialog import CreateProfileDialog
from ..userInterface.message_box_factory import MessageBoxFactory


class ProfileCreator(QDialog):

    def __init__(self, profile_manager_dialog, qgis_path, profile_manager, profile_handler, error_text, *args, **kwargs):
        super(ProfileCreator, self).__init__(*args, **kwargs)

        self.dlg = profile_manager_dialog
        self.profile_manager = profile_manager
        self.profile_handler = profile_handler
        self.message_box_factory = MessageBoxFactory(self.dlg)
        self.qgis_path = qgis_path
        self.qgs_profile_manager = QgsUserProfileManager(self.qgis_path)
        self.error_text = error_text

    def create_new_profile(self):
        """Creates new profile with user inputs name"""
        dialog = CreateProfileDialog(self.dlg, self.profile_handler)
        dialog.exec_()
        while not self.profile_handler.is_cancel_button_clicked and not self.profile_handler.is_ok_button_clicked:
            QCoreApplication.processEvents()

        if self.profile_handler.is_ok_button_clicked:
            with wait_cursor():
                profile_name = dialog.text_input.text()
                if profile_name == "":
                    self.message_box_factory.create_message_box(self.tr("Could not create profile"), self.tr("No profilename specified!"))
                else:
                    self.qgs_profile_manager.createUserProfile(profile_name)
                    try:
                        if self.profile_manager.operating_system is "mac":
                            profile_path = self.qgis_path + "/" + profile_name + "/qgis.org/"
                        else:
                            profile_path = self.qgis_path + "/" + profile_name + "/QGIS/"

                        profile_path = self.profile_manager.adjust_to_operating_system(profile_path)
                        mkdir(profile_path)

                        ini_path = profile_path + self.profile_manager.adjust_to_operating_system('QGIS3.ini')
                        qgis_ini_file = open(ini_path, "w")
                        qgis_ini_file.close()

                        self.message_box_factory.create_message_box(self.tr("Success"), self.tr("Profile successfully created!"),
                                                                    self.tr("New Profile"))
                    except FileExistsError:
                        self.message_box_factory.create_message_box(self.error_text, self.tr("Profile Directory already exists!"))