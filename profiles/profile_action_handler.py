from .profile_remover import ProfileRemover
from .profile_creator import ProfileCreator
from .profile_editor import ProfileEditor
from .profile_copier import ProfileCopier
from qgis.PyQt.QtWidgets import QDialog


class ProfileActionHandler(QDialog):

    def __init__(self, profile_manager_dialog, qgis_path, profile_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.is_cancel_button_clicked = False
        self.is_ok_button_clicked = False
        self.dlg = profile_manager_dialog
        self.qgis_path = qgis_path
        self.error_text = self.tr("Error")
        self.profile_manager = profile_manager
        self.profile_remover = ProfileRemover(self.dlg, self.qgis_path, self.profile_manager, self, self.error_text)
        self.profile_creator = ProfileCreator(self.dlg, self.qgis_path, self.profile_manager, self, self.error_text)
        self.profile_editor = ProfileEditor(self.dlg, self.qgis_path, self.profile_manager, self, self.error_text)
        self.profile_copier = ProfileCopier(self.dlg, self.qgis_path, self.profile_manager, self, self.error_text)

    def create_new_profile(self):
        """Creates a new profile"""
        self.profile_creator.create_new_profile()
        self.reset_button_state()
        self.profile_manager.interface_handler.init_profile_selection()

    def copy_profile(self):
        """Copies the selected profile"""
        self.profile_copier.copy_profile()
        self.reset_button_state()
        self.profile_manager.interface_handler.init_profile_selection()

    def edit_profile(self):
        """Edits the selected profile"""
        self.profile_editor.edit_profile()
        self.reset_button_state()
        self.profile_manager.interface_handler.init_profile_selection()

    def remove_profile(self):
        """Removes the selected profile"""
        self.profile_remover.remove_profile()
        self.reset_button_state()
        self.profile_manager.interface_handler.init_profile_selection()

    def reset_button_state(self):
        """Reset buttons state"""
        self.is_cancel_button_clicked = False
        self.is_ok_button_clicked = False
