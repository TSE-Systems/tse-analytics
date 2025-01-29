from pathlib import Path

from PySide6.QtWidgets import QDialog, QWidget

from tse_analytics.core.helper import get_available_sqlite_tables
from tse_analytics.modules.phenomaster.io.tse_import_settings import TseImportSettings
from tse_analytics.views.import_tse_dialog_ui import Ui_ImportTseDialog


class ImportTseDialog(QDialog):
    def __init__(self, path: Path, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_ImportTseDialog()
        self.ui.setupUi(self)

        tables = get_available_sqlite_tables(path)

        self.ui.checkBoxCaloBin.setEnabled("calo_bin" in tables)
        self.ui.checkBoxDrinkFeedBin.setEnabled("drinkfeed_bin" in tables)
        self.ui.checkBoxActiMotRaw.setEnabled("actimot_raw" in tables)

    def get_import_settings(self) -> TseImportSettings:
        import_settings = TseImportSettings(
            import_calo_bin=self.ui.checkBoxCaloBin.isChecked(),
            import_drinkfeed_bin=self.ui.checkBoxDrinkFeedBin.isChecked(),
            import_actimot_raw=self.ui.checkBoxActiMotRaw.isChecked(),
        )
        return import_settings
