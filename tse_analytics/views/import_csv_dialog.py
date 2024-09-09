from pathlib import Path

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QDialog, QWidget

from tse_analytics.core.csv_import_settings import CsvImportSettings
from tse_analytics.views.import_csv_dialog_ui import Ui_ImportCsvDialog


class ImportCsvDialog(QDialog):
    def __init__(self, path: Path, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_ImportCsvDialog()
        self.ui.setupUi(self)

        self.ui.buttonBox.accepted.connect(self._save_preferences)

        self.settings = QSettings()
        csv_import_settings: CsvImportSettings = self.settings.value(
            "CsvImportSettings", CsvImportSettings.get_default()
        )

        with open(path) as f:
            content = f.read(1024 * 1024)
            self.ui.plainTextEditOverview.setPlainText(content)

        self.ui.lineEditDelimiter.setText(csv_import_settings.delimiter)
        self.ui.checkBoxDayFirst.setChecked(csv_import_settings.day_first)
        self.ui.lineEditDateTimeFormat.setText(csv_import_settings.datetime_format)
        self.ui.groupBoxDateTimeFormat.setChecked(csv_import_settings.use_datetime_format)
        if csv_import_settings.decimal_separator == ",":
            self.ui.radioButtonComma.setChecked(True)
        else:
            self.ui.radioButtonPoint.setChecked(True)

    def _save_preferences(self):
        decimal_separator = "." if self.ui.radioButtonPoint.isChecked() else ","

        csv_import_settings = CsvImportSettings(
            self.ui.lineEditDelimiter.text(),
            decimal_separator,
            self.ui.checkBoxDayFirst.isChecked(),
            self.ui.groupBoxDateTimeFormat.isChecked(),
            self.ui.lineEditDateTimeFormat.text(),
        )

        self.settings.setValue("CsvImportSettings", csv_import_settings)
