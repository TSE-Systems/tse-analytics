from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QDialog, QWidget

from tse_analytics.core.csv_import_settings import CsvImportSettings
from tse_analytics.views.preferences_dialog_ui import Ui_PreferencesDialog


class PreferencesDialog(QDialog):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_PreferencesDialog()
        self.ui.setupUi(self)

        self.ui.buttonBox.accepted.connect(self.__save_preferences)

        self.settings = QSettings()
        csv_import_settings: CsvImportSettings = self.settings.value("CsvImportSettings", CsvImportSettings.get_default())

        self.ui.lineEditDelimiter.setText(csv_import_settings.delimiter)
        self.ui.checkBoxDayFirst.setChecked(csv_import_settings.day_first)
        self.ui.lineEditDateTimeFormat.setText(csv_import_settings.datetime_format)
        self.ui.groupBoxDateTimeFormat.setChecked(csv_import_settings.use_datetime_format)
        if csv_import_settings.decimal_separator == ",":
            self.ui.radioButtonComma.setChecked(True)
        else:
            self.ui.radioButtonPoint.setChecked(True)

    def __save_preferences(self):
        decimal_separator = "." if self.ui.radioButtonPoint.isChecked() else ","

        csv_import_settings = CsvImportSettings(
            self.ui.lineEditDelimiter.text(),
            decimal_separator,
            self.ui.checkBoxDayFirst.isChecked(),
            self.ui.groupBoxDateTimeFormat.isChecked(),
            self.ui.lineEditDateTimeFormat.text()
        )

        self.settings.setValue("CsvImportSettings", csv_import_settings)
