from configparser import RawConfigParser
from shutil import rmtree

from qgis.PyQt.QtCore import QObject, Qt
from qgis.PyQt.QtWidgets import QMessageBox


class PluginRemover(QObject):

    def __init__(self, profile_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.profile_manager = profile_manager
        self.parser = RawConfigParser()
        self.parser.optionxform = str
        self.source_qgis_ini_file = ""
        self.target_qgis_ini_file = ""
        self.checked_items = []
        self.plugin_list_widget = self.profile_manager.dlg.list_plugins

    def remove_plugins(self):
        """Removes all enabled plugins"""
        self.parser.clear()
        self.parser.read(self.source_qgis_ini_file)

        self.plugin_list_widget = self.profile_manager.dlg.list_plugins
        for item in self.plugin_list_widget.findItems("", Qt.MatchContains | Qt.MatchRecursive):
            plugin_name = item.text()
            if item.checkState() == Qt.Checked:
                self.checked_items.append(plugin_name)

                # Removes plugin from active state list in PythonPlugins Section
                if self.parser.has_option("PythonPlugins", plugin_name):
                    self.parser.remove_option("PythonPlugins", plugin_name)

                profile_paths = self.profile_manager.get_profile_paths()

                source_plugins_dir = self.profile_manager.adjust_to_operating_system(
                    profile_paths["source"] + 'python/plugins/' + plugin_name + '/')

                try:
                    rmtree(source_plugins_dir)
                except Exception as e:
                    QMessageBox.critical(
                        None,
                        self.tr("Plugin could not be deleted"),
                        self.tr("Plugin '{0}' could not be deleted due to error:\n{1}").format(plugin_name, e)
                    )
                    continue

        with open(self.source_qgis_ini_file, 'w') as qgisconf:
            self.parser.write(qgisconf)

    def set_ini_paths(self, source, target):
        self.source_qgis_ini_file = source
        self.target_qgis_ini_file = target
