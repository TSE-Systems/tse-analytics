from pathlib import Path

from PySide6.QtWidgets import QDialog, QWidget

from tse_analytics.core.utils import get_available_sqlite_tables
from tse_analytics.modules.phenomaster.io import tse_import_settings
from tse_analytics.modules.phenomaster.views.import_tse_dialog_ui import Ui_ImportTseDialog


class ImportTseDialog(QDialog):
    def __init__(self, path: Path, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_ImportTseDialog()
        self.ui.setupUi(self)

        tables = get_available_sqlite_tables(path)

        self.ui.checkBoxCaloBin.setEnabled(tse_import_settings.CALO_BIN_TABLE in tables)
        self.ui.checkBoxDrinkFeedBin.setEnabled(tse_import_settings.DRINKFEED_BIN_TABLE in tables)
        self.ui.checkBoxDrinkFeedRaw.setEnabled(tse_import_settings.DRINKFEED_RAW_TABLE in tables)
        self.ui.checkBoxActiMotRaw.setEnabled(tse_import_settings.ACTIMOT_RAW_TABLE in tables)
        self.ui.checkBoxGroupHousing.setEnabled(tse_import_settings.GROUP_HOUSING_TABLE in tables)

    def get_import_settings(self) -> tse_import_settings.TseImportSettings:
        import_settings = tse_import_settings.TseImportSettings(
            import_calo_bin=self.ui.checkBoxCaloBin.isChecked(),
            import_drinkfeed_bin=self.ui.checkBoxDrinkFeedBin.isChecked(),
            import_drinkfeed_raw=self.ui.checkBoxDrinkFeedRaw.isChecked(),
            import_actimot_raw=self.ui.checkBoxActiMotRaw.isChecked(),
            import_grouphousing=self.ui.checkBoxGroupHousing.isChecked(),
        )
        return import_settings
