from configparser import RawConfigParser
from os import path
from pathlib import Path
from shutil import copytree

from ...utils import adjust_to_operating_system


def import_plugins(
        source_profile_path: str,
        target_profile_path: str,
        target_qgis_ini_file: str,
        plugin_names: list[str],
):
    """Copies the specified plugins from source to target profile.

    Copies the files and sets the INI options accordingly.
    Imported plugins are always set to be active.

    Note: Plugin specific settings are not copied as we have no way of knowing where or how they are stored.

    Plugins are stored in python/plugins/
    Their active state is tracked in QGIS/QGIS3.ini's [PythonPlugins] section, e.g.:
    ...
    [PythonPlugins]
    ...
    fooPlugin=true
    PluggyBar=true
    BaZ=false
    ...

    Args:
        TODO
    """
    ini_parser = RawConfigParser()
    ini_parser.optionxform = str  # str = case-sensitive option names
    ini_parser.read(target_qgis_ini_file)

    if not ini_parser.has_section("PythonPlugins"):
        ini_parser["PythonPlugins"] = {}

    for plugin_name in plugin_names:
        ini_parser.set("PythonPlugins", plugin_name, "true")

        source_plugin_dir = adjust_to_operating_system(source_profile_path + 'python/plugins/' + plugin_name + '/')
        target_plugin_dir = adjust_to_operating_system(target_profile_path + 'python/plugins/' + plugin_name + '/')

        if path.exists(source_plugin_dir):
            if not path.exists(target_profile_path + 'python/plugins/'):
                Path(target_profile_path + 'python/plugins/').mkdir(parents=True, exist_ok=True)
            if not path.isdir(target_plugin_dir):
                copytree(source_plugin_dir, target_plugin_dir)
        else:
            continue  # TODO error, dont skip silently!

    with open(target_qgis_ini_file, 'w') as qgisconf:
        ini_parser.write(qgisconf, space_around_delimiters=False)
