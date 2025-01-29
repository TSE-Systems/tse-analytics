from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QCloseEvent, QKeyEvent
from PySide6.QtWidgets import QDialog, QWidget

from tse_analytics.modules.intellicage.data.intellicage_dataset import IntelliCageDataset
from tse_analytics.modules.intellicage.views.intellicage_dialog_ui import Ui_IntelliCageDialog
from tse_analytics.modules.intellicage.views.intellicage_preprocessed_data_widget import (
    IntelliCagePreprocessedDataWidget,
)
from tse_analytics.modules.intellicage.views.intellicage_raw_data_widget import IntelliCageRawDataWidget


class IntelliCageDialog(QDialog):
    def __init__(self, dataset: IntelliCageDataset, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_IntelliCageDialog()
        self.ui.setupUi(self)

        settings = QSettings()
        self.restoreGeometry(settings.value("IntelliCageDialog/Geometry"))

        self.dataset = dataset

        self.raw_data_widget = IntelliCageRawDataWidget(self.dataset.intellicage_data.raw_data, self)
        self.ui.tabWidget.addTab(self.raw_data_widget, "Raw Data")

        self.preprocessed_view = IntelliCagePreprocessedDataWidget(self.dataset, self)
        self.ui.tabWidget.addTab(self.preprocessed_view, "Preprocessed Data")

        self.ui.toolButtonPreprocess.clicked.connect(self._preprocess)
        self.ui.toolButtonExport.clicked.connect(self._export_data)

    def _preprocess(self) -> None:
        pass

    def _export_data(self):
        pass

    def hideEvent(self, event: QCloseEvent) -> None:
        settings = QSettings()
        settings.setValue("IntelliCageDialog/Geometry", self.saveGeometry())

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Escape:
            return
        super().keyPressEvent(event)
