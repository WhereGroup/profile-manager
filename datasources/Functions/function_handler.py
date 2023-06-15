from configparser import RawConfigParser

from qgis.core import Qgis, QgsMessageLog


class FunctionHandler:
    """Handler for importing custom expression functions, as stored in QGIS/QGIS3.ini's [expressions] section.

    E.g.
    ...
    [expressions]
    ...
    user\test_expression\expression=1 + 1
    user\test_expression\helpText="..."
    ...

    Note: This does not handle Python expression functions.
    """

    def __init__(self, profile_manager):
        self.profile_manager = profile_manager
        self.parser = RawConfigParser()
        self.parser.optionxform = str
        self.source_qgis_ini_file = None
        self.target_qgis_ini_file = None

    def import_functions(self):
        """Gets functions from source ini file and inserts them in target ini file

        Returns:
            error_message (str): An error message, if something failed.
        """
        QgsMessageLog.logMessage(f"Importing expression functions...", "Profile Manager", Qgis.Info)
        self.parser.clear()
        self.parser.read(self.source_qgis_ini_file)
        try:
            get_functions = dict(self.parser.items("expressions"))

            self.parser.clear()
            self.parser.read(self.target_qgis_ini_file)

            if not self.parser.has_section("expressions"):
                self.parser["expressions"] = {}

            for entry in get_functions:
                if "expression" in entry or "helpText" in entry:
                    self.parser.set("expressions", entry, get_functions[entry])
                    QgsMessageLog.logMessage(f"Found '{entry}'", "Profile Manager", Qgis.Info)

            with open(self.target_qgis_ini_file, 'w') as qgisconf:
                self.parser.write(qgisconf)
        except Exception as e:
            # TODO: It would be nice to have a smaller and more specific try block but until then we except broadly
            error = f"{type(e)}: {str(e)}"
            QgsMessageLog.logMessage(error, "Profile Manager", level=Qgis.Warning)
            return error

    def set_path_files(self, source_qgis_ini_file, target_qgis_ini_file):
        """Sets file paths"""
        self.source_qgis_ini_file = source_qgis_ini_file
        self.target_qgis_ini_file = target_qgis_ini_file
