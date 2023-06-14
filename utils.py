from contextlib import contextmanager

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QCursor, QGuiApplication


@contextmanager
def wait_cursor():
    try:
        QGuiApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        yield
    finally:
        QGuiApplication.restoreOverrideCursor()
