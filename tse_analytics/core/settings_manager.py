"""
Settings manager module for TSE Analytics.

This module provides functions for retrieving application settings from QSettings.
"""

from PySide6.QtCore import QSettings

from tse_analytics.core.csv_import_settings import CsvImportSettings


def get_csv_import_settings() -> CsvImportSettings:
    """
    Get the CSV import settings from application settings.

    This function retrieves the CSV import settings from QSettings if they exist,
    or returns the default settings if they don't.

    Returns:
        A CsvImportSettings object with the current settings.
    """
    settings = QSettings()
    result: CsvImportSettings = settings.value("CsvImportSettings", CsvImportSettings.get_default())
    return result
