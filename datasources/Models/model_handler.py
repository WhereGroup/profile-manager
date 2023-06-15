from os import listdir, path
from pathlib import Path
from shutil import copy2


class ModelHandler:
    """Handler for importing Processing models, as stored in processing/models/ .

    Note: Existing scripts with identical filenames will be overwritten!

    E.g.
    processing/models/my_model.model3
    processing/models/das.model3
    ...
    """

    def __init__(self, profile_manager):
        self.profile_manager = profile_manager
        self.source_model_dir = ""
        self.target_model_dir = ""

    def import_models(self):
        if path.exists(self.source_model_dir):
            if not path.exists(self.target_model_dir):
                Path(self.target_model_dir).mkdir(parents=True, exist_ok=True)
            for item in listdir(self.source_model_dir):
                source = path.join(self.source_model_dir, item)
                dest = path.join(self.target_model_dir, item)
                if path.isdir(source):
                    continue
                else:
                    copy2(source, dest)
        else:
            pass

    def set_path_files(self, source_model_dir, target_model_dir):
        self.source_model_dir = source_model_dir
        self.target_model_dir = target_model_dir
