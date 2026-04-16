"""
Entry point module for running the TSE Analytics package as a script.
"""

import os
import platform
import sys
from multiprocessing import freeze_support

from loguru import logger
from PySide6.QtCore import QSettings
from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import QApplication

from tse_analytics.core.workers.task_manager import TaskManager
from tse_analytics.globals import IS_RELEASE, init_global_settings
from tse_analytics.views.main_window import MainWindow


class App(QApplication):
    """
    Main application class for TSE Analytics.

    This class extends QApplication to provide TSE Analytics specific functionality,
    including application styling, organization information, and task management.
    """

    def __init__(self):
        """
        Initialize the TSE Analytics application.
        """

        QApplication.__init__(self)

        # Check platform
        if platform.system() == "Windows":
            import ctypes

            app_id = "tse-systems.tse-analytics"  # arbitrary string
            # Specifies a unique application-defined Application User Model ID (AppUserModelID) that identifies the current process to the taskbar.
            # This identifier allows an application to group its associated processes and windows under a single taskbar button.
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

        self.setStyle("fusion")
        self.setOrganizationName("TSE Systems")
        self.setOrganizationDomain("https://www.tse-systems.com")
        self.setApplicationName("TSE Analytics")
        self.setWindowIcon(QIcon(":/icons/app.ico"))

        # Force the light mode
        self.styleHints().setColorScheme(Qt.ColorScheme.Light)

        init_global_settings()

        # Set the selected stylesheet
        settings = QSettings()
        appStyle = settings.value("appStyle", "tse-light")
        if IS_RELEASE:
            style_file = os.path.join(os.path.dirname(sys.executable), f"_internal/styles/qss/{appStyle}.css")
        else:
            style_file = os.path.join(os.path.dirname(__file__), f"styles/qss/{appStyle}.css")
        with open(style_file) as file:
            self.setStyleSheet(file.read())

        # TaskManager singleton initialization
        TaskManager(self)


def handle_exception(exc_type, exc_value, exc_traceback) -> None:
    """
    Global exception handler for uncaught exceptions.

    This function is set as the sys.excepthook to catch and log any uncaught exceptions
    that occur during the application's execution.

    Args:
        exc_type: The type of the exception.
        exc_value: The exception instance.
        exc_traceback: The traceback object.

    Returns:
        None
    """
    # logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    logger.opt(exception=(exc_type, exc_value, exc_traceback)).critical("Uncaught exception")


if __name__ == "__main__":
    # See https://docs.python.org/3/library/multiprocessing.html#multiprocessing.freeze_support
    freeze_support()

    # See: https://github.com/pyinstaller/pyinstaller/issues/7334#issuecomment-1357447176
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w")

    logger.remove()  # Remove all handlers added so far, including the default one.
    logger.add(sys.stderr, level="INFO", colorize=True, backtrace=False, enqueue=True)

    sys.excepthook = handle_exception

    app = App()

    main_window = MainWindow(sys.argv)
    main_window.show()

    sys.exit(app.exec())
