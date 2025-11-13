"""
Utility functions module for TSE Analytics.

This module provides various utility functions used throughout the TSE Analytics
application, including functions for working with images, SQLite databases,
Qt widgets, and time conversions.
"""

from base64 import b64encode
from datetime import time
from io import BytesIO
from pathlib import Path

import connectorx as cx
import pandas as pd
import seaborn.objects as so
from matplotlib.figure import Figure
from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import QSizePolicy, QToolButton, QWidget, QWidgetAction

IS_RELEASE = Path("_internal").exists()

CSV_IMPORT_ENABLED = True


def get_html_image_from_figure(figure: Figure) -> str:
    """
    Convert a matplotlib figure to an HTML image tag with embedded base64 data.

    This function saves the figure as a PNG image in memory, encodes it as base64,
    and returns an HTML img tag that can be used to display the image in HTML content.

    Args:
        figure: The matplotlib Figure object to convert.

    Returns:
        A string containing an HTML img tag with the figure embedded as base64 data.
    """
    io = BytesIO()
    figure.savefig(io, format="png")
    encoded = b64encode(io.getvalue()).decode("utf-8")
    return f"<img src='data:image/png;base64,{encoded}'><br/>"


def get_html_image_from_plot(plot: so.Plot) -> str:
    io = BytesIO()
    plot.save(io, format="png", bbox_inches="tight")
    encoded = b64encode(io.getvalue()).decode("utf-8")
    return f"<img src='data:image/png;base64,{encoded}'><br/>"


def get_html_table(df: pd.DataFrame, caption: str, precision=5, index=True) -> str:
    styler = df.style.set_caption(caption).format(precision=precision)
    if not index:
        styler = styler.hide(axis="index")
    return styler.to_html()


def get_available_sqlite_tables(path: Path) -> list[str]:
    """
    Get a list of all table names in a SQLite database file.

    This function connects to the specified SQLite database file and retrieves
    the names of all tables defined in the database.

    Args:
        path: The path to the SQLite database file.

    Returns:
        A list of strings containing the names of all tables in the database.
    """
    df = cx.read_sql(
        f"sqlite:///{path}",
        "SELECT name FROM sqlite_master WHERE type='table';",
        return_type="pandas",
    )
    return df["name"].tolist()


def get_widget_tool_button(parent: QWidget, widget: QWidget, text: str, icon: QIcon) -> QToolButton:
    """
    Create a QToolButton with a widget in its popup menu.

    This function creates a QToolButton that displays the specified text and icon,
    and shows the specified widget when clicked. The widget is added to the button's
    popup menu as a QWidgetAction.

    Args:
        parent: The parent widget for the button and widget action.
        widget: The widget to display in the popup menu.
        text: The text to display on the button.
        icon: The icon to display on the button.

    Returns:
        A configured QToolButton that shows the widget when clicked.
    """
    button = QToolButton(
        parent,
        popupMode=QToolButton.ToolButtonPopupMode.InstantPopup,
        toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
    )
    button.setText(text)
    button.setIcon(icon)

    widget_action = QWidgetAction(parent)
    widget_action.setDefaultWidget(widget)
    button.addAction(widget_action)
    return button


def get_h_spacer_widget(parent: QWidget) -> QWidget:
    """
    Create a horizontal spacer widget for use in layouts.

    This function creates a widget with an expanding horizontal size policy
    and a minimum vertical size policy, which can be used as a spacer in
    horizontal layouts to push other widgets to the sides.

    Args:
        parent: The parent widget for the spacer.

    Returns:
        A QWidget configured as a horizontal spacer.
    """
    widget = QWidget(parent)
    widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
    return widget


def time_to_float(value: time) -> float:
    """
    Convert a time object to a float representing hours.

    This function converts a datetime.time object to a float value representing
    the time in hours, with minutes converted to a fractional part of an hour.
    For example, 2:30 PM would be converted to 14.5.

    Args:
        value: The time object to convert.

    Returns:
        A float representing the time in hours.
    """
    return value.hour + value.minute / 60.0
