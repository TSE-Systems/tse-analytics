"""
Main application module for TSE Analytics.

This module initializes the application, sets up global configurations for various
libraries (matplotlib, PyQtGraph, pandas, seaborn), and provides the main entry point
for the TSE Analytics application.
"""

import ctypes
import os
import sys

import matplotlib
import pandas as pd
import seaborn as sns
from PySide6.QtCore import QSettings
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from loguru import logger
from pyqtgraph import setConfigOptions

from tse_analytics.core.utils import IS_RELEASE
from tse_analytics.core.workers.task_manager import TaskManager
from tse_analytics.views.main_window import MainWindow

# Global configuration

matplotlib.use("QtAgg")

# Global PyQtGraph settings
setConfigOptions(
    imageAxisOrder="row-major",
    foreground="d",
    background="w",
    leftButtonPan=True,
    antialias=False,
    useOpenGL=False,
)

pd.options.mode.copy_on_write = "warn"
# pd.options.mode.copy_on_write = True
# pd.options.future.infer_string = True
pd.set_option("colheader_justify", "center")  # FOR TABLE <th>
# pd.set_option("display.precision", 3)

sns.set_theme(style="whitegrid")
sns.set_color_codes("pastel")


class App(QApplication):
    """
    Main application class for TSE Analytics.

    This class extends QApplication to provide TSE Analytics specific functionality,
    including application styling, organization information, and task management.
    """

    def __init__(self, args):
        """
        Initialize the TSE Analytics application.

        Args:
            args: Command line arguments passed to the application.
        """
        # Force the light mode
        args += ["-platform", "windows:darkmode=1"]

        app_id = "tse-systems.tse-analytics"  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

        QApplication.__init__(self, args)
        self.setStyle("fusion")
        self.setOrganizationName("TSE Systems")
        self.setOrganizationDomain("https://www.tse-systems.com")
        self.setApplicationName("TSE Analytics")
        self.setWindowIcon(QIcon(":/icons/app.ico"))

        # Set selected stylesheet
        settings = QSettings()
        appStyle = settings.value("appStyle", "tse-light")
        style_file = f"_internal/styles/qss/{appStyle}.css" if IS_RELEASE else f"styles/qss/{appStyle}.css"
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


def main() -> None:
    """
    Main entry point for the TSE Analytics application.

    This function initializes logging, sets up exception handling, creates the
    application instance, shows the main window, and starts the application's
    event loop.

    Returns:
        None
    """
    # See: https://github.com/pyinstaller/pyinstaller/issues/7334#issuecomment-1357447176
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w")

    logger.remove()  # Remove all handlers added so far, including the default one.
    logger.add(sys.stderr, level="INFO", colorize=True, backtrace=False, enqueue=True)

    sys.excepthook = handle_exception

    app = App(sys.argv)

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())
