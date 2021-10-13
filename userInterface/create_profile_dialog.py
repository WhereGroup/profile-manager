from qgis.PyQt.QtWidgets import QLineEdit, QDialogButtonBox, QVBoxLayout, QDialog
from PyQt5.QtCore import Qt


class CreateProfileDialog(QDialog):

    def __init__(self, profile_manager_dialog, profile_action_handler, only_edit=False, *args, **kwargs):
        """Sets up dialog with input field"""
        super(CreateProfileDialog, self).__init__(*args, **kwargs)

        self.dlg = profile_manager_dialog
        self.profile_action_handler = profile_action_handler

        self.rename = ""
        self.create = ""
        self.translate()

        if only_edit:
            self.setWindowTitle(self.rename)
        else:
            self.setWindowTitle(self.create)

        self.layout = QVBoxLayout()

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Name")
        self.QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(self.QBtn)
        self.button_box.accepted.connect(self.ok_button_clicked)
        self.button_box.rejected.connect(self.cancel_button_clicked)

        self.layout.addWidget(self.text_input, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.button_box, alignment=Qt.AlignCenter)
        self.setLayout(self.layout)
    
    def cancel_button_clicked(self):
        """Called when cancel was clicked"""
        self.profile_action_handler.is_cancel_button_clicked = True
        self.done(0)

    def ok_button_clicked(self):
        """Called when OK was clicked"""
        self.profile_action_handler.is_ok_button_clicked = True
        self.done(0)

    def translate(self):
        self.rename = self.tr("Rename Profile!")
        self.create = self.tr("Create Profile!")

