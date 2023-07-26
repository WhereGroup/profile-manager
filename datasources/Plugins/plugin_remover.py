from configparser import RawConfigParser
from shutil import rmtree

from qgis.PyQt.QtWidgets import QMessageBox

from ...utils import adjust_to_operating_system, tr


def remove_plugins(
        profile_path: str,
        qgis_ini_file: str,
        plugin_names: list[str],
):
    """Removes the specified plugins from the profile.

    Removes both the files from python/plugins/ and the QGIS/QGIS3.ini [PythonPlugins] section entries.

    Note: Plugin specific settings are not removed as we have no way of knowing where or how they are stored.

    Args:
        TODO
    """
    ini_parser = RawConfigParser()
    ini_parser.optionxform = str  # str = case-sensitive option names
    ini_parser.read(qgis_ini_file)

    for plugin_name in plugin_names:
        # Removes plugin from active state list in PythonPlugins section
        if ini_parser.has_option("PythonPlugins", plugin_name):
            ini_parser.remove_option("PythonPlugins", plugin_name)

        plugins_dir = adjust_to_operating_system(profile_path + 'python/plugins/' + plugin_name + '/')

        try:
            rmtree(plugins_dir)
        except OSError as e:
            # TODO do not do GUI stuff in these functions if possible, maybe return a list of errors instead?
            QMessageBox.critical(
                None,
                tr("Plugin could not be removed"),
                tr("Plugin '{0}' could not be removed due to error:\n{1}").format(plugin_name, e)
            )
            continue

    with open(qgis_ini_file, 'w') as qgisconf:
        ini_parser.write(qgisconf, space_around_delimiters=False)
