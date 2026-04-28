"""
This module initializes the application, sets up global configurations for various
libraries (matplotlib, PyQtGraph, pandas, seaborn), and provides the main entry point
for the TSE Analytics application.
"""

import sys

import matplotlib as mpl
import seaborn as sns
import seaborn.objects as so
from pyqtgraph import setConfigOptions
from PySide6.QtCore import QSettings

IS_RELEASE = getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")

INTERNAL_ENABLED = False

LAYOUT_VERSION = 15
MAX_RECENT_FILES = 10

TIME_RESOLUTION_UNIT = "ms"


def init_global_settings():
    settings = QSettings()

    dpi = settings.value("DPI", 96)
    figure_width = settings.value("FigureWidth", 13.0)
    figure_height = settings.value("FigureHeight", 9.5)

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
