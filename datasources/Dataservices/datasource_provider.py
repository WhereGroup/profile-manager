# -*- coding: utf-8 -*-

from configparser import RawConfigParser
from re import compile, search
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QTreeWidgetItem
from urllib.parse import unquote


class DataSourceProvider:

    def __init__(self, path, profile_manager):
        self.dlg = profile_manager
        self.parser = RawConfigParser()
        self.parser.optionxform = str
        self.ini_path = path
        self.service_name_regex = compile(r'\\(.*?)\\')
        self.dictionary_of_checked_web_sources = {}
        self.dictionary_of_checked_database_sources = {}

    def update_path(self, path):
        """Sets .ini path"""
        self.ini_path = path

    def get_data_sources(self, compile_string, item_name, is_source):
        """Gets Web connections and displays them in the treeWidget"""
        self.parser.clear()
        self.parser.read(self.ini_path)

        search_string = compile(compile_string)
        data_sources_parent = QTreeWidgetItem([item_name])
        if is_source:
            data_sources_parent.setFlags(data_sources_parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

        try:
            for key in self.parser['qgis']:
                if search_string.search(key):
                    source_name_raw = search(self.service_name_regex, key)
                    source_name = source_name_raw.group(0).replace("\\", "")

                    source_name = unquote(source_name, 'latin-1')

                    data_sources_child = QTreeWidgetItem([source_name])
                    if is_source:
                        data_sources_child.setFlags(data_sources_child.flags() | Qt.ItemIsUserCheckable)
                        data_sources_child.setCheckState(0, Qt.Unchecked)

                    data_sources_parent.addChild(data_sources_child)
        except:
            return None

        if data_sources_parent.childCount() is 0:
            data_sources_parent = None

        return data_sources_parent

    def get_data_base(self, compile_string, item_name, service_block, is_source):
        """Gets DB connections and displays them in the treeWidget"""
        self.parser.clear()
        self.parser.read(self.ini_path)

        search_string = compile(compile_string)

        data_base_sources_parent = QTreeWidgetItem([item_name])
        if is_source:
            data_base_sources_parent.setFlags(data_base_sources_parent.flags() | Qt.ItemIsTristate
                                              | Qt.ItemIsUserCheckable)

        if item_name == "GeoPackage":
            self.service_name_regex = compile(r'\\(.+).\\')

        try:
            for key in self.parser[service_block]:
                if search_string.search(key):
                    db_name_raw = search(self.service_name_regex, key)
                    if item_name == "GeoPackage":
                        db_name = db_name_raw.group(0).replace("\\GPKG\\connections\\", "").replace("\\", "")
                    else:
                        db_name = db_name_raw.group(0).replace("\\", "")

                    db_name = unquote(db_name, 'latin-1')

                    data_base_sources_child = QTreeWidgetItem([db_name])
                    if is_source:
                        data_base_sources_child.setFlags(data_base_sources_child.flags() | Qt.ItemIsUserCheckable)
                        data_base_sources_child.setCheckState(0, Qt.Unchecked)

                    data_base_sources_parent.addChild(data_base_sources_child)
        except:
            return None

        if data_base_sources_parent.childCount() is 0:
            data_base_sources_parent = None

        return data_base_sources_parent

    def init_checked_sources(self):
        """"Loops trough sources and stores checked ones in the dict"""

        self.dictionary_of_checked_web_sources = {
            "WMS": [],
            "WFS": [],
            "WCS": [],
            "XYZ": [],
            "ArcGisMapServer": [],
            "ArcGisFeatureServer": [],
            "GeoNode": [],
        }

        self.dictionary_of_checked_database_sources = {
            "providers": [],
            "SpatiaLite": [],
            "PostgreSQL": [],
            "MSSQL": [],
            "DB2": [],
            "Oracle": [],
        }

        for item in self.dlg.treeWidgetSource.findItems("", Qt.MatchContains | Qt.MatchRecursive):
            if item.childCount() == 0 and item.checkState(0) == Qt.Checked:
                if item.parent().text(0) in self.dictionary_of_checked_database_sources:
                    self.dictionary_of_checked_database_sources[item.parent().text(0)].append(item.text(0))
                elif item.parent().text(0) == "GeoPackage":
                    self.dictionary_of_checked_database_sources["providers"].append(item.text(0))
                else:
                    self.dictionary_of_checked_web_sources[item.parent().text(0)].append(item.text(0))
