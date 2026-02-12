"""
Help documentation manager module for TSE Analytics.

This module provides functions for displaying online and offline help documentation.
"""

from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices

from tse_analytics.core.utils import IS_RELEASE


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
    current_directory = Path.cwd()
    docs_directory = current_directory / "_internal/docs" if IS_RELEASE else current_directory.parent / "docs"
    help_index = docs_directory / "index.html"
    QDesktopServices.openUrl(QUrl.fromLocalFile(help_index))
