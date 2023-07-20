from os import listdir, path
from pathlib import Path
from shutil import copy2


def import_scripts(source_profile_path: str, target_profile_path: str):
    """Imports Processing scripts from source to target profile.

    Note: Existing scripts with identical filenames will be overwritten!

    Scripts are stored in the processing/scripts/ subdirectory of a profile, e.g.:
    ...
    processing/scripts/my_great_processing_script.py
    processing/scripts/snakes.py
    ...

    Args:
        TODO
    """
    source_scripts_dir = source_profile_path + "processing/scripts/"
    target_scripts_dir = target_profile_path + "processing/scripts/"
    if path.exists(source_scripts_dir):
        if not path.exists(target_scripts_dir):
            Path(target_scripts_dir).mkdir(parents=True, exist_ok=True)
        for item in listdir(source_scripts_dir):
            source = path.join(source_scripts_dir, item)
            dest = path.join(target_scripts_dir, item)
            if path.isdir(source):
                continue
            else:
                copy2(source, dest)
    else:
        pass
