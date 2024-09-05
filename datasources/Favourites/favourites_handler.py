from configparser import RawConfigParser

from qgis.core import Qgis, QgsMessageLog


def import_favourites(source_qgis_ini_file, target_qgis_ini_file):
    """Imports browser favourites from source to target profile.

    Favourites are stored in QGIS/QGIS3.ini's [browser] section, e.g.:
    ...
    [browser]
    favourites=/path/to|||My favourite folder!, /tmp/test|||title, ...
    ...

    Args:
        TODO

    Returns:
        error_message (str): An error message, if something XML related failed.
    """
    source_ini_parser = RawConfigParser()
    source_ini_parser.optionxform = str  # str = case-sensitive option names
    source_ini_parser.read(source_qgis_ini_file)

    try:
        get_favourites = dict(source_ini_parser.items("browser"))

        favourites_to_be_imported = {}
        favourites_to_be_preserved = ""

        for entry in get_favourites:
            if entry == "favourites":
                favourites_to_be_imported[entry] = get_favourites[entry]

        target_ini_parser = RawConfigParser()
        target_ini_parser.optionxform = str  # str = case-sensitive option names
        target_ini_parser.read(target_qgis_ini_file)

        if not target_ini_parser.has_section("browser"):
            target_ini_parser["browser"] = {}
        elif target_ini_parser.has_option("browser", "favourites"):
            favourites_to_be_preserved = target_ini_parser.get("browser", "favourites")

        import_string = favourites_to_be_imported["favourites"].replace(favourites_to_be_preserved, "")

        target_ini_parser.set("browser", "favourites", favourites_to_be_preserved + import_string)

        with open(target_qgis_ini_file, 'w') as qgisconf:
            target_ini_parser.write(qgisconf, space_around_delimiters=False)
    except Exception as e:
        # TODO: It would be nice to have a smaller and more specific try block but until then we except broadly
        error = f"{type(e)}: {str(e)}"
        QgsMessageLog.logMessage(error, "Profile Manager", level=Qgis.Warning)
        return error
