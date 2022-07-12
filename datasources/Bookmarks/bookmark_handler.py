from lxml import etree as et
from pathlib import Path
import sys


class BookmarkHandler:

    def __init__(self, qgis_path, profile_manager):
        self.profile_manager = profile_manager
        self.qgis_path = qgis_path
        self.bookmark_list = []
        self.source_bookmark_file = ""
        self.target_bookmark_file = ""
        self.parser = et.XMLParser(remove_blank_text=True)

    def parse_source_bookmarks(self):
        """Parses bookmarks from source xml"""
        # get the element tree of the source file
        try:
            source_tree = et.parse(self.source_bookmark_file, self.parser)
            self.insert_bookmarks_to_target_profile(source_tree)
        except:
            print("Oops!", sys.exc_info()[0], "occurred.")

    def insert_bookmarks_to_target_profile(self, source_tree):
        """Inserts bookmarks into target xml file"""
        # check if target file exists
        self.check_if_file_exists()
        # get the element tree of the target file
        # fill if empty
        try:
            target_tree = et.parse(self.target_bookmark_file, self.parser)
        except et.XMLSyntaxError:
            with open(self.target_bookmark_file, "w") as xmlTarget:
                xmlTarget.write("<Bookmarks></Bookmarks>")

            target_tree = et.parse(self.target_bookmark_file, self.parser)

        # find all bookmark elements
        source_root_tag = source_tree.findall('Bookmark')

        # get the root element "Bookmarks"
        target_tree_root = target_tree.getroot()

        # Remove duplicate entries to prevent piling data
        target_tree_root = self.remove_duplicates(source_root_tag, target_tree, target_tree_root)

        # append the elements
        for element in source_root_tag:
            target_tree_root.append(element)

        # overwrite the xml file
        et.ElementTree(target_tree_root)\
            .write(self.target_bookmark_file, pretty_print=True, encoding='utf-8', xml_declaration=True)

    @staticmethod
    def remove_duplicates(source_toot_tag, target_tree, target_tree_root):
        """Removes duplicate entries"""
        target_root_tag = target_tree.findall('Bookmark')
        for s_element in source_toot_tag:
            for t_element in target_root_tag:
                if s_element.attrib["name"] == t_element.attrib["name"]:
                    target_tree_root.remove(t_element)

        return target_tree_root

    def check_if_file_exists(self):
        """Checks if file exists"""
        target_file = Path(self.target_bookmark_file)
        if target_file.is_file():
            pass
        else:
            self.create_new_file()

    def create_new_file(self):
        """Creates a new file"""
        new_file = open(self.target_bookmark_file, "w")
        new_file.write("<Bookmarks></Bookmarks>")
        new_file.close()

    def set_path_files(self, source_bookmark_file, target_bookmark_file):
        """Sets file path's"""
        self.source_bookmark_file = source_bookmark_file
        self.target_bookmark_file = target_bookmark_file






