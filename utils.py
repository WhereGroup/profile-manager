from contextlib import contextmanager
from sys import platform

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QCursor, QGuiApplication


@contextmanager
def wait_cursor():
    try:
        QGuiApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        yield
    finally:
        QGuiApplication.restoreOverrideCursor()


def adjust_to_operating_system(path_to_adjust):
    """Adjusts path to current OS.

    For MacOS it contains special logic to also replace the /QGIS/ -> /qgis.org/ directory name.
    """
    if platform.startswith('win32'):
        return path_to_adjust.replace("/", "\\")
    elif platform == "unix":
        return path_to_adjust.replace("\\", "/")
    elif platform == "darwin":  # macos
        return path_to_adjust.replace("\\", "/").replace("/QGIS/QGIS3.ini", "/qgis.org/QGIS3.ini")
    else:
        raise NotImplementedError("Unsupported platform '{platform}'")
