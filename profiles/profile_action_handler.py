from qgis.PyQt.QtWidgets import QDialog

from .profile_copier import ProfileCopier
from .profile_creator import ProfileCreator
from .profile_editor import ProfileEditor
from .profile_remover import ProfileRemover


class ProfileActionHandler(QDialog):

    def __init__(self, profile_manager_dialog, qgis_path, profile_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.is_cancel_button_clicked = False
        self.is_ok_button_clicked = False
        self.dlg = profile_manager_dialog
        self.qgis_path = qgis_path
        self.profile_manager = profile_manager
        self.profile_remover = ProfileRemover(self.dlg, self.qgis_path, self.profile_manager)
        self.profile_creator = ProfileCreator(self.qgis_path, self.profile_manager)
        self.profile_editor = ProfileEditor(self.dlg, self.qgis_path, self.profile_manager)
        self.profile_copier = ProfileCopier(self.dlg, self.qgis_path)

    def create_new_profile(self):
        """Creates a new profile"""
        self.profile_creator.create_new_profile()
        self.profile_manager.interface_handler.populate_profile_listings()

    def copy_profile(self):
        """Copies the selected profile"""
        self.profile_copier.copy_profile()
        self.profile_manager.interface_handler.populate_profile_listings()

    def edit_profile(self):
        """Edits the selected profile"""
        self.profile_editor.edit_profile()
        self.profile_manager.interface_handler.populate_profile_listings()

    def remove_profile(self):
        """Removes the selected profile"""
        self.profile_remover.remove_profile()
        self.profile_manager.interface_handler.populate_profile_listings()
