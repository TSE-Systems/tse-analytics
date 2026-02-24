import pandas as pd
from pyqttoast import ToastPreset
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QCheckBox, QLabel, QSpinBox, QToolBar, QWidget

from tse_analytics.core import manager
from tse_analytics.core.toaster import make_toast
from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset
from tse_analytics.modules.phenomaster.submodules.grouphousing.data.processor import preprocess_trafficage_datatable
from tse_analytics.modules.phenomaster.submodules.grouphousing.views.activity_widget import ActivityWidget
from tse_analytics.modules.phenomaster.submodules.grouphousing.views.grouphousing_widget_ui import Ui_GroupHousingWidget
from tse_analytics.modules.phenomaster.submodules.grouphousing.views.heatmap.heatmap_widget import HeatmapWidget
from tse_analytics.modules.phenomaster.submodules.grouphousing.views.preprocessed_data.preprocessed_data_widget import (
    PreprocessedDataWidget,
)
from tse_analytics.modules.phenomaster.submodules.grouphousing.views.raw_data.raw_data_widget import RawDataWidget


class GroupHousingWidget(QWidget):
    def __init__(self, dataset: PhenoMasterDataset, parent: QWidget):
        super().__init__(parent)

        self.ui = Ui_GroupHousingWidget()
        self.ui.setupUi(self)

        self.setWindowFlags(
            Qt.WindowType.Window
            # | Qt.WindowType.CustomizeWindowHint
            # | Qt.WindowType.WindowTitleHint
            # | Qt.WindowType.WindowCloseButtonHint
        )

        # settings = QSettings()

        self.dataset = dataset

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
        toolbar.addWidget(self.checkBoxRemoveRepeatingRecords)

        self.checkBoxRemoveOverlappingRecords = QCheckBox("Remove Overlapping Records", toolbar)
        self.checkBoxRemoveOverlappingRecords.setChecked(False)
        self.checkBoxRemoveOverlappingRecords.checkStateChanged.connect(
            lambda state: self.overlapping_timediff_spin_box.setEnabled(state == Qt.CheckState.Checked)
        )
        toolbar.addWidget(self.checkBoxRemoveOverlappingRecords)

        toolbar.addWidget(QLabel("Time diff [ms]:"))
        self.overlapping_timediff_spin_box = QSpinBox(
            toolbar,
            minimum=1000,
            maximum=10000,
            singleStep=250,
            value=1500,
        )
        self.overlapping_timediff_spin_box.setEnabled(False)
        toolbar.addWidget(self.overlapping_timediff_spin_box)

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

    def _update_tabs(self) -> None:
        is_preprocessed = self.preprocessed_df is not None
        self.ui.tabWidget.setTabVisible(self.preprocessed_data_tab_index, is_preprocessed)
        self.ui.tabWidget.setTabVisible(self.activity_tab_index, is_preprocessed)
        self.ui.tabWidget.setTabVisible(self.heatmap_tab_index, is_preprocessed)

    def _preprocess(self) -> None:
        self.preprocessed_df = self.dataset.grouphousing_data.get_preprocessed_data(
            self.checkBoxRemoveRepeatingRecords.isChecked(),
            self.checkBoxRemoveOverlappingRecords.isChecked(),
            self.overlapping_timediff_spin_box.value(),
        )
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

        make_toast(
            self,
            "Group Housing",
            "TraffiCage table added.",
            duration=2000,
            preset=ToastPreset.INFORMATION,
            show_duration_bar=True,
        ).show()
