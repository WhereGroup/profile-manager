# -*- coding: utf-8 -*-

from qgis.PyQt.QtWidgets import QVBoxLayout, QDialog, QLabel, QDialogButtonBox
from PyQt5.QtCore import Qt


class RemoveSourcesDialog(QDialog):

    def __init__(self, profile_manager_dialog, profile_manager, back_up_path, *args, **kwargs):
        """Sets up dialog with input field"""
        super(RemoveSourcesDialog, self).__init__(*args, **kwargs)

        self.dlg = profile_manager_dialog
        self.profile_manager = profile_manager

        self.setWindowTitle(self.tr("Remove Sources!"))
        self.layout = QVBoxLayout()

        removal_info_text = self.tr("Are you sure you want to delete these sources?\n\nA backup will be created at ") \
                            + back_up_path
        self.profile_name_label = QLabel()
        self.profile_name_label.setText(removal_info_text)
        self.q_btn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(self.q_btn)
        self.button_box.accepted.connect(self.ok_button_clicked)
        self.button_box.rejected.connect(self.cancel_button_clicked)

        self.layout.addWidget(self.profile_name_label, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.button_box, alignment=Qt.AlignCenter)
        self.setLayout(self.layout)

    def cancel_button_clicked(self):
        """Called when cancel was clicked"""
        self.profile_manager.is_cancel_button_clicked = True
        self.done(0)

    def ok_button_clicked(self):
        """Called when OK was clicked"""
        self.profile_manager.is_ok_button_clicked = True
        self.done(0)

