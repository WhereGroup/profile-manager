from pathlib import Path
from sys import platform
from typing import Any, Dict, List, Optional
from configparser import NoSectionError, RawConfigParser


from qgis.core import QgsUserProfileManager
from qgis.utils import iface


def qgis_profiles_path() -> Path:
    """Get QGIS profiles paths from current platforms

    - Windows : $HOME / "AppData" / "Roaming" / "QGIS" / "QGIS3" / "profiles"
    - MacOS : $HOME / "Library" / "Application Support" / "QGIS" / "QGIS3" / "profiles"
    - Linux : $HOME / ".local" / "share" / "QGIS" / "QGIS3" / "profiles"

    Returns:
        Path: QGIS profiles path
    """
    home_path = Path.home()
    # Windows
    if platform.startswith("win32"):
        return home_path / "AppData" / "Roaming" / "QGIS" / "QGIS3" / "profiles"
    # MacOS
    if platform == "darwin":
        return (
            home_path
            / "Library"
            / "Application Support"
            / "QGIS"
            / "QGIS3"
            / "profiles"
        )
    # Linux
    return home_path / ".local" / "share" / "QGIS" / "QGIS3" / "profiles"


def get_profile_qgis_ini_path(profile_name: str) -> Path:
    """Get QGIS3.ini file path for a profile

    Args:
        profile_name (str): profile name

    Returns:
        Path: QGIS3.ini path
    """
    # MacOS
    if platform.startswith("darwin"):
        return qgis_profiles_path() / profile_name / "qgis.org" / "QGIS3.ini"
    # Windows / Linux
    return qgis_profiles_path() / profile_name / "QGIS" / "QGIS3.ini"


def get_profile_plugin_metadata_path(profile_name: str, plugin_slug_name: str) -> Path:
    """Get path to metadata.txt for a plugin inside a profile

    Args:
        profile_name (str): profile name
        plugin_slug_name (str): plugin slug name

    Returns:
        Path: metadata.txt path
    """
    return (
        qgis_profiles_path()
        / profile_name
        / "python"
        / "plugins"
        / plugin_slug_name
        / "metadata.txt"
    )


def get_installed_plugin_list(
    profile_name: str, only_activated: bool = True
) -> List[str]:
    """Get installed plugin for a profile

    Args:
        profile_name (str): profile name
        only_activated (bool, optional): True to get only activated plugin, False to get all installed plugins. Defaults to True.

    Returns:
        List[str]: plugin slug name list
    """
    ini_parser = RawConfigParser()
    ini_parser.optionxform = str  # str = case-sensitive option names
    ini_parser.read(get_profile_qgis_ini_path(profile_name))
    try:
        plugins_in_profile = dict(ini_parser.items("PythonPlugins"))
    except NoSectionError:
        plugins_in_profile = {}

    if only_activated:
        return [key for key, value in plugins_in_profile.items() if value == "true"]
    else:
        return plugins_in_profile.keys()


def get_installed_plugin_metadata(
    profile_name: str, plugin_slug_name: str
) -> Dict[str, Any]:
    """Get metadata information from metadata.txt file in profile installed plugin

    Args:
        profile_name (str): profile name
        plugin_slug_name (str): plugin slug name

    Returns:
        Dict[str, Any]: metadata as dict. Empty dict if metadata unavailable
    """
    ini_parser = RawConfigParser()
    ini_parser.optionxform = str  # str = case-sensitive option names
    ini_parser.read(get_profile_plugin_metadata_path(profile_name, plugin_slug_name))
    try:
        metadata = dict(ini_parser.items("general"))
    except NoSectionError:
        metadata = {}
    return metadata


def get_plugin_info_from_qgis_manager(
    plugin_slug_name: str,
) -> Optional[Dict[str, str]]:
    """Get plugin informations from QGIS plugin manager

    Args:
        plugin_slug_name (str): plugin slug name

    Returns:
        Optional[Dict[str, str]]: metadata from plugin manager, None if plugin not found
    """
    return iface.pluginManagerInterface().pluginMetadata(plugin_slug_name)


def get_profile_name_list() -> List[str]:
    """Get profile name list from current installed QGIS

    Returns:
        List[str]: profile name list
    """
    return QgsUserProfileManager(qgis_profiles_path()).allProfiles()
