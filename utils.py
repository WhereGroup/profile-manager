from contextlib import contextmanager
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication, QCursor


@contextmanager
def wait_cursor():
    try:
        QGuiApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        yield
    finally:
        QGuiApplication.restoreOverrideCursor()