# -*- coding: utf-8 -*-

from pathlib import Path
from os import path, listdir
from shutil import copytree, copy2


class ScriptHandler:

    def __init__(self, profile_manager):
        self.profile_manager = profile_manager
        self.source_scripts_dir = ""
        self.target_scripts_dir = ""

    def import_scripts(self):
        if path.exists(self.source_scripts_dir):
            if not path.exists(self.target_scripts_dir):
                Path(self.target_scripts_dir).mkdir(parents=True, exist_ok=True)
            for item in listdir(self.source_scripts_dir):
                source = path.join(self.source_scripts_dir, item)
                dest = path.join(self.target_scripts_dir, item)
                if path.isdir(source):
                    continue
                else:
                    copy2(source, dest)
        else:
            pass

    def set_path_files(self, source_model_dir, target_model_dir):
        self.source_scripts_dir = source_model_dir
        self.target_scripts_dir = target_model_dir
