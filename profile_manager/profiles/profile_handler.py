import re
from os import rename
from pathlib import Path
from shutil import copytree, rmtree
from sys import platform

from qgis.core import QgsApplication, QgsUserProfileManager

from profile_manager.profiles.utils import qgis_profiles_path

# validation rule from QGIS' QgsUserProfileSelectionDialog
VALID_PROJECT_NAME_REGEX = "[^/\\\\]+"


def create_profile(profile_name: str):
    """Creates new profile"""
    if not profile_name:
        raise ValueError("Empty profile name provided")
    if not re.match(VALID_PROJECT_NAME_REGEX, profile_name):
        raise ValueError("Invalid profile name")

    qgs_profile_manager = QgsUserProfileManager(str(qgis_profiles_path()))
    qgs_profile_manager.createUserProfile(profile_name)

    # Right now there is only the profile directory and the qgis.db in its root.
    # We want to be able to write things to the profile's QGIS3.ini file so:
    if platform == "darwin":
        sub_dir = "qgis.org"
    else:
        sub_dir = "QGIS"
    ini_dir_path = qgis_profiles_path() / profile_name / sub_dir
    ini_dir_path.mkdir()
    ini_path = ini_dir_path / "QGIS3.ini"
    ini_path.touch()


def remove_profile(profile_name: str):
    """Removes profile"""
    if not profile_name:
        raise ValueError("Empty profile name provided")
    if not re.match(VALID_PROJECT_NAME_REGEX, profile_name):
        raise ValueError("Invalid profile name")
    if profile_name == Path(QgsApplication.qgisSettingsDirPath()).name:
        raise ValueError("Cannot remove the profile that is currently active")

    profile_path = qgis_profiles_path() / profile_name
    rmtree(profile_path)


def copy_profile(source_profile_name: str, target_profile_name: str):
    if not source_profile_name:
        raise ValueError("Empty source profile name provided")
    if not target_profile_name:
        raise ValueError("Empty target profile name provided")
    if not re.match(VALID_PROJECT_NAME_REGEX, source_profile_name):
        raise ValueError("Invalid source profile name")
    if not re.match(VALID_PROJECT_NAME_REGEX, target_profile_name):
        raise ValueError("Invalid target profile name")
    if source_profile_name == target_profile_name:
        raise ValueError("Cannot copy profile to itself")

    source_profile_path = qgis_profiles_path() / source_profile_name
    profile_path = qgis_profiles_path() / target_profile_name

    copytree(source_profile_path, profile_path)


def rename_profile(old_profile_name: str, new_profile_name: str):
    """Renames profile to new name."""
    if not old_profile_name:
        raise ValueError("Empty old profile name provided")
    if not old_profile_name:
        raise ValueError("Empty new profile name provided")
    if not re.match(VALID_PROJECT_NAME_REGEX, old_profile_name):
        raise ValueError("Invalid old profile name")
    if not re.match(VALID_PROJECT_NAME_REGEX, new_profile_name):
        raise ValueError("Invalid new profile name")
    if old_profile_name == Path(QgsApplication.qgisSettingsDirPath()).name:
        raise ValueError("Cannot rename the profile that is currently active")

    profile_before_change = qgis_profiles_path() / old_profile_name
    profile_after_change = qgis_profiles_path() / new_profile_name

    rename(profile_before_change, profile_after_change)
