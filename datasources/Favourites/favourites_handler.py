from configparser import RawConfigParser

from qgis.core import Qgis, QgsMessageLog


class FavouritesHandler:
    """Handler for importing browser favourites, as stored in QGIS/QGIS3.ini's [browser] section.

    E.g.:
    ...
    [browser]
    favourites=/path/to|||My favourite folder!, /tmp/test|||title, ...
    ...
    """

    def __init__(self):
        self.source_qgis_ini_file = None
        self.target_qgis_ini_file = None

    def import_favourites(self):
        """Gets favourites from ini file and inserts them in target file.

        Returns:
            error_message (str): An error message, if something XML related failed.
        """
        source_ini_parser = RawConfigParser()
        source_ini_parser.optionxform = str  # str = case-sensitive option names
        source_ini_parser.read(self.source_qgis_ini_file)

        try:
            get_favourites = dict(source_ini_parser.items("browser"))

            favourites_to_be_imported = {}
            favourites_to_be_preserved = ""

            for entry in get_favourites:
                if entry == "favourites":
                    favourites_to_be_imported[entry] = get_favourites[entry]

            target_ini_parser = RawConfigParser()
            target_ini_parser.optionxform = str  # str = case-sensitive option names
            target_ini_parser.read(self.target_qgis_ini_file)

            if not target_ini_parser.has_section("browser"):
                target_ini_parser["browser"] = {}
            elif target_ini_parser.has_option("browser", "favourites"):
                favourites_to_be_preserved = target_ini_parser.get("browser", "favourites")

            import_string = favourites_to_be_imported["favourites"].replace(favourites_to_be_preserved, "")

            target_ini_parser.set("browser", "favourites", favourites_to_be_preserved + import_string)

            with open(self.target_qgis_ini_file, 'w') as qgisconf:
                target_ini_parser.write(qgisconf, space_around_delimiters=False)
        except Exception as e:
            # TODO: It would be nice to have a smaller and more specific try block but until then we except broadly
            error = f"{type(e)}: {str(e)}"
            QgsMessageLog.logMessage(error, "Profile Manager", level=Qgis.Warning)
            return error

    def set_path_files(self, source_qgis_ini_file, target_qgis_ini_file):
        """Sets file paths"""
        self.source_qgis_ini_file = source_qgis_ini_file
        self.target_qgis_ini_file = target_qgis_ini_file
