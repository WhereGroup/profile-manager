from contextlib import contextmanager

from qgis.PyQt.QtCore import QCoreApplication, Qt
from qgis.PyQt.QtGui import QCursor, QGuiApplication


@contextmanager
def wait_cursor():
    try:
        QGuiApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        yield
    finally:
        QGuiApplication.restoreOverrideCursor()


def tr(message):
    # for translating in non-QObject class contexts
    return QCoreApplication.translate("ProfileManager", message)
