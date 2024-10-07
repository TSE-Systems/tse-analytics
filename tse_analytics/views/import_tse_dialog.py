from pathlib import Path

from PySide6.QtWidgets import QDialog, QWidget

from tse_analytics.core.helper import get_available_sqlite_tables
from tse_analytics.core.tse_import_settings import TseImportSettings
from tse_analytics.views.import_tse_dialog_ui import Ui_ImportTseDialog


class ImportTseDialog(QDialog):
    def __init__(self, path: Path, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_ImportTseDialog()
        self.ui.setupUi(self)

        tables = get_available_sqlite_tables(path)

        self.ui.checkBoxCalo.setEnabled("calo_bin" in tables)
        self.ui.checkBoxMeal.setEnabled("drinkfeed_bin" in tables)
        self.ui.checkBoxActiMot.setEnabled("actimot_raw" in tables)


    def get_import_settings(self) -> TseImportSettings:
        import_settings = TseImportSettings(
            import_calo=self.ui.checkBoxCalo.isChecked(),
            import_meal=self.ui.checkBoxMeal.isChecked(),
            import_actimot=self.ui.checkBoxActiMot.isChecked(),
        )
        return import_settings
