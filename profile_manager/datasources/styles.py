import sqlite3
from pathlib import Path
from shutil import copy


def import_styles(source_profile_path: Path, target_profile_path: Path):
    """Imports styles from source profile to target profile.

    Note: Currently it only imports symbols (not 3D) and label settings, not 3D symbols, color ramps, tags, etc.

    Styles are stored in symbology-style.db.

    Args:
        source_profile_path: Path of profile directory to import from
        target_profile_path: Path of profile directory to import to
    """
    source_db_path = source_profile_path / "symbology-style.db"
    target_db_path = target_profile_path / "symbology-style.db"

    # try if we can straight up copy the file to the target profile
    if not target_db_path.is_file():
        copy(source_db_path, target_db_path)
        return

    # target file exists, so we transfer styles via SQL
    source_db = sqlite3.connect(source_db_path)
    target_db = sqlite3.connect(target_db_path)

    source_db_cursor = source_db.cursor()
    target_db_cursor = target_db.cursor()

    # import label settings
    custom_labels = source_db_cursor.execute("SELECT * FROM labelsettings")
    target_db_cursor.executemany(
        "INSERT OR REPLACE INTO labelsettings VALUES (?, ?, ?, ?)", custom_labels
    )

    # import symbols
    # FIXME: This has a hard-coded assumption that symbols with ids <= 115 are builtin symbols,
    #        this will fail as soon as a new builtin symbol is shipped by QGIS.
    custom_symbols = source_db_cursor.execute("SELECT * FROM symbol WHERE id > 115")
    target_db_cursor.executemany(
        "INSERT OR REPLACE INTO symbol VALUES (?, ?, ?, ?)", custom_symbols
    )

    source_db.commit()
    target_db.commit()

    source_db.close()
    target_db.close()
