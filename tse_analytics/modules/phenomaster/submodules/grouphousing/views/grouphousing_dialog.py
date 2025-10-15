import pandas as pd
from PySide6.QtCore import QSettings, Qt, QSize
from PySide6.QtGui import QCloseEvent, QIcon
from PySide6.QtWidgets import QWidget, QToolBar, QCheckBox

from tse_analytics.core import manager
from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset
from tse_analytics.modules.phenomaster.submodules.grouphousing.data.processor import preprocess_trafficage_datatable
from tse_analytics.modules.phenomaster.submodules.grouphousing.views.activity_widget import ActivityWidget
from tse_analytics.modules.phenomaster.submodules.grouphousing.views.grouphousing_dialog_ui import Ui_GroupHousingDialog
from tse_analytics.modules.phenomaster.submodules.grouphousing.views.heatmap_widget.heatmap_widget import HeatmapWidget
from tse_analytics.modules.phenomaster.submodules.grouphousing.views.preprocessed_data_widget.preprocessed_data_widget import (
    PreprocessedDataWidget,
)
from tse_analytics.modules.phenomaster.submodules.grouphousing.views.raw_data_widget.raw_data_widget import (
    RawDataWidget,
)


class GroupHousingDialog(QWidget):
    def __init__(self, dataset: PhenoMasterDataset, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_GroupHousingDialog()
        self.ui.setupUi(self)

        self.setWindowFlags(
            Qt.WindowType.Window
            # | Qt.WindowType.CustomizeWindowHint
            # | Qt.WindowType.WindowTitleHint
            # | Qt.WindowType.WindowCloseButtonHint
        )

        settings = QSettings()
        self.restoreGeometry(settings.value("GroupHousingDialog/Geometry"))

        self.dataset = dataset
        self._remove_repeating_records = True

        # Setup toolbar
        toolbar = QToolBar(
            "Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.preprocess_action = toolbar.addAction(QIcon(":/icons/preprocess.png"), "Preprocess")
        self.preprocess_action.triggered.connect(self._preprocess)
        self.add_datatable_action = toolbar.addAction(QIcon(":/icons/icons8-insert-table-16.png"), "Add Datatable...")
        self.add_datatable_action.setEnabled(False)
        self.add_datatable_action.triggered.connect(self._add_datatable)

        self.checkBoxRemoveRepeatingRecords = QCheckBox("Remove Repeating Records", toolbar)
        self.checkBoxRemoveRepeatingRecords.setChecked(True)
        self.checkBoxRemoveRepeatingRecords.checkStateChanged.connect(self._remove_repeating_records_changed)
        toolbar.addWidget(self.checkBoxRemoveRepeatingRecords)

        self.ui.verticalLayout.insertWidget(0, toolbar)

        self.raw_data_widget = RawDataWidget(self.dataset.grouphousing_data, self)
        self.ui.tabWidget.addTab(self.raw_data_widget, "Raw Data")

        self.preprocessed_view = PreprocessedDataWidget(self.dataset.grouphousing_data, self)
        self.preprocessed_data_tab_index = self.ui.tabWidget.addTab(self.preprocessed_view, "Preprocessed Data")

        self.activity_widget = ActivityWidget(self)
        self.activity_tab_index = self.ui.tabWidget.addTab(self.activity_widget, "Activity")

        self.heatmap_widget = HeatmapWidget(self.dataset.grouphousing_data, self)
        self.heatmap_tab_index = self.ui.tabWidget.addTab(self.heatmap_widget, "Heatmap")

        self.preprocessed_df: dict[str, pd.DataFrame] | None = None

        self._update_tabs()

    def _update_tabs(self):
        is_preprocessed = self.preprocessed_df is not None
        self.ui.tabWidget.setTabVisible(self.preprocessed_data_tab_index, is_preprocessed)
        self.ui.tabWidget.setTabVisible(self.activity_tab_index, is_preprocessed)
        self.ui.tabWidget.setTabVisible(self.heatmap_tab_index, is_preprocessed)

    def _preprocess(self) -> None:
        self.preprocessed_df = self.dataset.grouphousing_data.get_preprocessed_data(self._remove_repeating_records)
        self.preprocessed_view.set_preprocessed_data(self.preprocessed_df)
        self.activity_widget.set_preprocessed_data(self.dataset.grouphousing_data, self.preprocessed_df)
        self.heatmap_widget.set_preprocessed_data(self.preprocessed_df)
        self._update_tabs()
        self.add_datatable_action.setEnabled(True)

    def _add_datatable(self) -> None:
        if self.preprocessed_df is None or "TraffiCage" not in self.preprocessed_df:
            return

        datatable = preprocess_trafficage_datatable(self.dataset, self.preprocessed_df["TraffiCage"])
        manager.add_datatable(datatable)

    def _remove_repeating_records_changed(self, state: Qt.CheckState) -> None:
        self._remove_repeating_records = state == Qt.CheckState.Checked

    def closeEvent(self, event: QCloseEvent) -> None:
        settings = QSettings()
        settings.setValue("GroupHousingDialog/Geometry", self.saveGeometry())
