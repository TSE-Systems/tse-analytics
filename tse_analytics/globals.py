"""
This module initializes the application, sets up global configurations for various
libraries (matplotlib, PyQtGraph, pandas, seaborn), and provides the main entry point
for the TSE Analytics application.
"""

import sys
from pathlib import Path

import matplotlib as mpl
import seaborn as sns
import seaborn.objects as so
from pyqtgraph import setConfigOptions
from PySide6.QtCore import QSettings

IS_RELEASE = getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")

# True when running inside a Flatpak sandbox (/.flatpak-info is always present there).
IS_FLATPAK = Path("/.flatpak-info").exists()


def get_resource_base() -> Path:
    """Absolute base directory for bundled resource folders (styles, docs, ...).

    Returns ``<executable dir>/_internal`` for a frozen PyInstaller build, and the
    ``tse_analytics`` package directory for a source checkout. Resources must be resolved
    against this rather than the current working directory, which is undefined at runtime
    (e.g. ``/`` inside a Flatpak sandbox).
    """
    if IS_RELEASE:
        return Path(sys.executable).parent / "_internal"
    return Path(__file__).parent


INTERNAL_ENABLED = False

LAYOUT_VERSION = 15
MAX_RECENT_FILES = 10

TIME_RESOLUTION_UNIT = "ms"


def init_global_settings():
    settings = QSettings()

    # Pass explicit type= so values round-trip as numbers on Linux, where the QSettings INI
    # backend returns everything as strings (unlike the typed Windows registry backend).
    dpi = settings.value("DPI", 96, type=int)
    figure_width = settings.value("FigureWidth", 13.0, type=float)
    figure_height = settings.value("FigureHeight", 9.5, type=float)

    # Global PyQtGraph settings
    setConfigOptions(
        imageAxisOrder="row-major",
        foreground="d",
        background="w",
        leftButtonPan=True,
        antialias=False,
        useOpenGL=False,
    )

    # Global Pandas settings
    # pd.set_option("display.colheader_justify", "center")  # FOR TABLE <th>
    # pd.set_option("display.precision", 3)

    # Global Matplotlib settings
    mpl.use("QtAgg")
    mpl.rcParams["figure.dpi"] = dpi
    mpl.rcParams["figure.figsize"] = figure_width, figure_height

    # Global Seaborn settings
    # sns.objects.Plot.config.display["format"] = "svg"
    so.Plot.config.theme.update(sns.axes_style("whitegrid"))
    sns.set_theme(style="whitegrid")
    sns.set_color_codes("pastel")
