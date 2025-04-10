from PySide6.QtCore import QSettings

from tse_analytics.core.csv_import_settings import CsvImportSettings

settings = QSettings()


def get_csv_import_settings() -> CsvImportSettings:
    result: CsvImportSettings = settings.value("CsvImportSettings", CsvImportSettings.get_default())
    return result
