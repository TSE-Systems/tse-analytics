from PySide6.QtCore import QSettings

from tse_analytics.core.csv_import_settings import CsvImportSettings


def get_csv_import_settings() -> CsvImportSettings:
    settings = QSettings()
    result: CsvImportSettings = settings.value("CsvImportSettings", CsvImportSettings.get_default())
    return result
