from os import listdir, path
from pathlib import Path
from shutil import copy2


def import_models(source_profile_path: str, target_profile_path: str):
    """Imports Processing models from source to target profile.

    Note: Existing models with identical filenames will be overwritten!

    Models are stored in the processing/models/ subdirectory of a profile, e.g.:
    ...
    processing/models/my_model.model3
    processing/models/das.model3
    ...

    Args:
        TODO
    """
    source_models_dir = source_profile_path + "processing/models/"
    target_models_dir = target_profile_path + "processing/models/"

    if path.exists(source_models_dir):
        if not path.exists(target_models_dir):
            Path(target_models_dir).mkdir(parents=True, exist_ok=True)
        for item in listdir(source_models_dir):
            source = path.join(source_models_dir, item)
            dest = path.join(target_models_dir, item)
            if path.isdir(source):
                continue
            else:
                copy2(source, dest)
    else:
        pass
