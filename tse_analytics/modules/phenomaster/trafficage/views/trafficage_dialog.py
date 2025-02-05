from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QCloseEvent, QKeyEvent
from PySide6.QtWidgets import QDialog, QWidget, QFileDialog

from tse_analytics.modules.phenomaster.data.pm_dataset import PMDataset
from tse_analytics.modules.phenomaster.trafficage.views.trafficage_activity_widget import TraffiCageActivityWidget
from tse_analytics.modules.phenomaster.trafficage.views.trafficage_dialog_ui import Ui_TraffiCageDialog
from tse_analytics.modules.phenomaster.trafficage.views.trafficage_heatmap_widget import TraffiCageHeatmapWidget
from tse_analytics.modules.phenomaster.trafficage.views.trafficage_preprocessed_data_widget import \
    TraffiCagePreprocessedDataWidget
from tse_analytics.modules.phenomaster.trafficage.views.trafficage_raw_data_widget import TraffiCageRawDataWidget


class TraffiCageDialog(QDialog):
    def __init__(self, dataset: PMDataset, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_TraffiCageDialog()
        self.ui.setupUi(self)

        settings = QSettings()
        self.restoreGeometry(settings.value("TraffiCageDialog/Geometry"))

        self.dataset = dataset

        self.raw_data_widget = TraffiCageRawDataWidget(self.dataset.trafficage_data, self)
        self.ui.tabWidget.addTab(self.raw_data_widget, "Raw Data")

        self.preprocessed_view = TraffiCagePreprocessedDataWidget(self.dataset, self)
        self.ui.tabWidget.addTab(self.preprocessed_view, "Preprocessed Data")

        self.activity_widget = TraffiCageActivityWidget(self)
        self.activity_widget.set_data(self.dataset.trafficage_data)
        self.ui.tabWidget.addTab(self.activity_widget, "Activity")

        self.heatmap_widget = TraffiCageHeatmapWidget(self.dataset, self)
        self.ui.tabWidget.addTab(self.heatmap_widget, "Heatmap")

        self.ui.toolButtonPreprocess.clicked.connect(self._preprocess)
        self.ui.toolButtonExport.clicked.connect(self._export_data)

    def _preprocess(self) -> None:
        pass

    def _export_data(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export to CSV", "", "CSV Files (*.csv)")
        if filename:
            self.dataset.trafficage_data.df.to_csv(filename, sep=";", index=False)

    def hideEvent(self, event: QCloseEvent) -> None:
        settings = QSettings()
        settings.setValue("TraffiCageDialog/Geometry", self.saveGeometry())

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Escape:
            return
        super().keyPressEvent(event)
