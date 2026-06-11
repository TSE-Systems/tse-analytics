"""
Help documentation manager module for TSE Analytics.

This module provides functions for displaying online and offline help documentation.
"""

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices

from tse_analytics.globals import IS_RELEASE, get_resource_base


def show_online_help():
    """
    Open the online help documentation in the default web browser.

    This function opens the TSE Analytics online documentation website
    using the system's default web browser.
    """
    QDesktopServices.openUrl("https://tse-systems.github.io/tse-analytics-docs")


def show_offline_help():
    """
    Open the offline help documentation in the default web browser.
    """
    base = get_resource_base()
    # Frozen: docs are bundled at <base>/docs; source: at the repo root (one level above the package).
    docs_directory = base / "docs" if IS_RELEASE else base.parent / "docs"
    help_index = docs_directory / "index.html"
    QDesktopServices.openUrl(QUrl.fromLocalFile(help_index))
