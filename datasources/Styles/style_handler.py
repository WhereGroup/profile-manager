import sqlite3

from os import path
from shutil import copy

from qgis.core import Qgis, QgsMessageLog


class StyleHandler:
    """Handler to import styles, as stored in symbology-style.db .

    Note: Currently only symbols and label settings are supported, not 3D symbols, color ramps, tags, etc.
    """

    def __init__(self):
        self.source_db = None
        self.target_db = None

        self.source_db_cursor = None
        self.target_db_cursor = None

    def set_db_connection(self, source_db_path, target_db_path):
        self.source_db = sqlite3.connect(source_db_path)

        if path.isfile(target_db_path) is False:
            copy(source_db_path, target_db_path.replace("symbology-style.db", ""))  # TODO remove unnecessary replace()
        self.target_db = sqlite3.connect(target_db_path)

        self.source_db_cursor = self.source_db.cursor()
        self.target_db_cursor = self.target_db.cursor()

    def import_styles(self):
        try:
            self.import_labels()
            self.import_symbols()

            self.source_db.commit()
            self.target_db.commit()

            self.source_db.close()
            self.target_db.close()
        except sqlite3.Error as e:
            QgsMessageLog.logMessage(str(e), "Profile Manager", level=Qgis.Warning)

    def import_symbols(self):
        # FIXME: This has a hard-coded assumption that symbols with ids <= 115 are builtin symbols,
        #        this will fail as soon as a new builtin symbol is shipped by QGIS.
        custom_symbols = self.source_db_cursor.execute('SELECT * FROM symbol WHERE id>115')

        self.target_db_cursor.executemany('INSERT OR REPLACE INTO symbol VALUES (?,?,?,?)', custom_symbols)

    def import_labels(self):
        custom_labels = self.source_db_cursor.execute('SELECT * FROM labelsettings')

        self.target_db_cursor.executemany('INSERT OR REPLACE INTO labelsettings VALUES (?,?,?,?)', custom_labels)
