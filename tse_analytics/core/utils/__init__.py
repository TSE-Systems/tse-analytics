"""Utility functions for TSE Analytics.

This package provides various utility functions used throughout the TSE Analytics
application, including functions for working with images, SQLite databases,
Qt widgets, and time conversions.
"""

from tse_analytics.core.utils.data import get_group_by_params, time_to_float
from tse_analytics.core.utils.database import get_available_sqlite_tables
from tse_analytics.core.utils.formatting import (
    get_great_table,
    get_html_image_from_figure,
    get_html_image_from_plot,
    get_html_table,
    get_plot_layout,
)
from tse_analytics.core.utils.ui import get_figsize_from_widget, get_h_spacer_widget, get_widget_tool_button

__all__ = [
    "get_available_sqlite_tables",
    "get_figsize_from_widget",
    "get_group_by_params",
    "get_h_spacer_widget",
    "get_html_image_from_figure",
    "get_html_image_from_plot",
    "get_html_table",
    "get_great_table",
    "get_plot_layout",
    "get_widget_tool_button",
    "time_to_float",
]
