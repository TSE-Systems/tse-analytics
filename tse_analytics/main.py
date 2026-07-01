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
from tse_analytics.globals import IS_FLATPAK, get_resource_base, init_global_settings
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
        # Bind to the installed .desktop file so the window maps to the correct taskbar
        # icon and application grouping. Only meaningful inside Flatpak, where the .desktop
        # file is installed; setting it elsewhere (e.g. a dev checkout) makes Qt's
        # xdg-portal registration warn that no app info exists for this app ID.
        if IS_FLATPAK:
            self.setDesktopFileName("io.github.TSE_Systems.tse_analytics")
        self.setWindowIcon(QIcon(":/icons/app.ico"))

        # Force the light mode
        self.styleHints().setColorScheme(Qt.ColorScheme.Light)

        init_global_settings()

        # Set the selected stylesheet
        settings = QSettings()
        appStyle = settings.value("appStyle", "tse-light")
        style_file = get_resource_base() / "styles" / "qss" / f"{appStyle}.css"
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
    Console-script entry point for TSE Analytics (see ``[project.scripts]``).

    Configures process-level settings, logging and the global exception hook,
    then constructs the application and main window and runs the Qt event loop.
    """
    # See https://docs.python.org/3/library/multiprocessing.html#multiprocessing.freeze_support
    freeze_support()

    if platform.system() == "Linux":
        # Qt selects its platform plugin when QApplication is constructed (below),
        # so this is set in time even though PySide6 is imported at module level.
        # Force xcb (X11 / XWayland) for reliable rendering, incl. inside Flatpak.
        # setdefault keeps any explicit override (e.g. QT_QPA_PLATFORM=wayland).
        os.environ.setdefault("QT_QPA_PLATFORM", "xcb")

        # Ignore the desktop's UI settings (font, palette, …) so dev rendering matches
        # the sandboxed Flatpak, which can't read dconf. Without this the GTK/GNOME
        # platform theme injects the desktop font ("Adwaita Sans 11") per widget class
        # (menus, headers, buttons, …), making the UI look heavier/larger than the
        # Flatpak. Must be called before the QApplication is constructed. The light
        # color scheme and the app's own QSS are applied explicitly in App.__init__.
        QApplication.setDesktopSettingsAware(False)

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


if __name__ == "__main__":
    main()
