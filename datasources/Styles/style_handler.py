# -*- coding: utf-8 -*-

from sqlite3 import connect
from os import path
from shutil import copy
import sys


class StyleHandler:

    def __init__(self):
        self.source_db = None
        self.target_db = None

        self.source_db_cursor = None
        self.target_db_cursor = None

    def set_db_connection(self, source_db_path, target_db_path):
        self.source_db = connect(source_db_path)
        if path.isfile(target_db_path) is False:
            copy(source_db_path, target_db_path.replace("symbology-style.db", ""))

        self.target_db = connect(target_db_path)

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
        except:
            print("Oops!", sys.exc_info()[0], "occurred.")

    def import_symbols(self):
        custom_symbols = self.source_db_cursor.execute('SELECT * FROM symbol WHERE id>115')

        self.target_db_cursor.executemany('INSERT OR REPLACE INTO symbol VALUES (?,?,?,?)', custom_symbols)

    def import_labels(self):
        custom_labels = self.source_db_cursor.execute('SELECT * FROM labelsettings')

        self.target_db_cursor.executemany('INSERT OR REPLACE INTO labelsettings VALUES (?,?,?,?)', custom_labels)


