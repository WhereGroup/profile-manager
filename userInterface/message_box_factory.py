# -*- coding: utf-8 -*-

from qgis.PyQt.QtWidgets import QMessageBox, QDialog


class MessageBoxFactory(QDialog):

    def __init__(self, profile_manager_dialog, *args, **kwargs):
        super(MessageBoxFactory, self).__init__(*args, **kwargs)
        self.dlg = profile_manager_dialog


    def create_message_box(self, text, informative_text, style="warning"):
        """Creates a dialog that displays an informative message"""
        msg_box = QMessageBox()
        text_top = str(text) + "                                                                     "
        msg_box.setText(text_top)
        msg_box.setInformativeText(informative_text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setEscapeButton(QMessageBox.Close)

        if style == "warning":
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle(self.tr("Warning!"))
        else:
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle(self.tr("Information"))

        msg_box.exec_()

