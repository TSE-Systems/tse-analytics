from dataclasses import dataclass

import pandas as pd
from pyqttoast import ToastPreset
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QComboBox, QFileDialog, QLabel, QSpinBox, QToolBar, QWidget

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_figsize_from_widget
from tse_analytics.core.workers import TaskManager, Worker
from tse_analytics.modules.intellicage.toolbox.learning_curve.processor import (
    BIN_MODE_TIME,
    BIN_MODE_VISIT,
    METRIC_CORRECT_VISITS,
    METRIC_LICKS_PER_VISIT,
    METRIC_NOSEPOKE_ERROR_RATE,
    METRIC_PLACE_ERROR_RATE,
    METRIC_REQUIRED_COLUMNS,
    IntelliCageLearningCurveResult,
    get_intellicage_learning_curve_result,
)
from tse_analytics.toolbox.toolbox_registry import toolbox_plugin
from tse_analytics.toolbox.toolbox_widget_base import ToolboxWidgetBase
from tse_analytics.views.misc.group_by_selector import GroupBySelector

_METRICS = [
    METRIC_CORRECT_VISITS,
    METRIC_PLACE_ERROR_RATE,
    METRIC_NOSEPOKE_ERROR_RATE,
    METRIC_LICKS_PER_VISIT,
]
_BIN_MODES = [BIN_MODE_TIME, BIN_MODE_VISIT]


@dataclass
class LearningCurveWidgetSettings:
    metric: str = METRIC_CORRECT_VISITS
    bin_mode: str = BIN_MODE_TIME
    bin_size: int = 24
    group_by: str = "Animal"


@toolbox_plugin(
    category="IntelliCage",
    label="Learning Curve",
    icon=":/icons/icons8-analyze-16.png",
    order=2,
    dataset_types=("IntelliCage", "IntelliMaze"),
)
class LearningCurveWidget(ToolboxWidgetBase):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(
            datatable,
            LearningCurveWidgetSettings,
            "Learning Curve",
            parent,
        )

        self.curve_data: pd.DataFrame | None = None
        self.summary: pd.DataFrame | None = None

    def _create_toolbar_items(self, toolbar: QToolBar) -> None:
        toolbar.addWidget(QLabel("Metric:"))
        self.metric_selector = QComboBox(toolbar)
        self.metric_selector.addItems(_METRICS)
        self.metric_selector.setCurrentText(self._settings.metric)
        toolbar.addWidget(self.metric_selector)
        toolbar.addSeparator()

        toolbar.addWidget(QLabel("Bin by:"))
        self.bin_mode_selector = QComboBox(toolbar)
        self.bin_mode_selector.addItems(_BIN_MODES)
        self.bin_mode_selector.setCurrentText(self._settings.bin_mode)
        self.bin_mode_selector.currentTextChanged.connect(self._on_bin_mode_changed)
        toolbar.addWidget(self.bin_mode_selector)

        self.bin_size_spinbox = QSpinBox(toolbar)
        self.bin_size_spinbox.setRange(1, 100000)
        self.bin_size_spinbox.setValue(self._settings.bin_size)
        toolbar.addWidget(self.bin_size_spinbox)
        self.bin_size_suffix_label = QLabel("")
        toolbar.addWidget(self.bin_size_suffix_label)
        self._on_bin_mode_changed(self.bin_mode_selector.currentText())
        toolbar.addSeparator()

        toolbar.addWidget(QLabel("Group by:"))
        self.group_by_selector = GroupBySelector(toolbar, self.datatable, selected_mode=self._settings.group_by)
        toolbar.addWidget(self.group_by_selector)
        toolbar.addSeparator()

        self.export_excel_action = toolbar.addAction(QIcon(":/icons/icons8-export-16.png"), "Export to Excel")
        self.export_excel_action.triggered.connect(self._export_to_excel)
        self.export_excel_action.setEnabled(False)

    def _on_bin_mode_changed(self, mode: str) -> None:
        self.bin_size_suffix_label.setText("h" if mode == BIN_MODE_TIME else "visits")

    def _get_settings_value(self):
        return LearningCurveWidgetSettings(
            self.metric_selector.currentText(),
            self.bin_mode_selector.currentText(),
            self.bin_size_spinbox.value(),
            self.group_by_selector.currentText(),
        )

    def _update(self) -> None:
        self.report_view.clear()
        self.curve_data = None
        self.summary = None

        settings = self._get_settings_value()

        needed = ["Animal", "Timedelta", *METRIC_REQUIRED_COLUMNS[settings.metric]]
        if settings.group_by != "Animal":
            needed.append(settings.group_by)
        missing = [c for c in needed if c not in self.datatable.df.columns]
        if missing:
            make_toast(
                self,
                self.title,
                f"This datatable is missing the column(s) {', '.join(missing)} required for "
                f"'{settings.metric}'. Open the IntelliCage Visits datatable.",
                duration=4000,
                preset=ToastPreset.WARNING,
            ).show()
            return

        columns = list(dict.fromkeys(needed))
        df = self.datatable.get_filtered_df(columns)
        df = df.dropna(subset=["Animal", "Timedelta"])

        if df.empty:
            make_toast(
                self,
                self.title,
                "No data to analyze.",
                duration=2000,
                preset=ToastPreset.WARNING,
            ).show()
            return

        self.update_action.setEnabled(False)
        self.export_excel_action.setEnabled(False)

        self.toast = make_toast(self, self.title, "Processing...")
        self.toast.show()

        worker = Worker(
            get_intellicage_learning_curve_result,
            self.datatable.dataset,
            df,
            settings.metric,
            settings.bin_mode,
            settings.bin_size,
            settings.group_by,
            get_figsize_from_widget(self.report_view),
        )
        worker.signals.result.connect(self._result)
        worker.signals.finished.connect(self._finished)
        TaskManager.start_task(worker)

    def _result(self, result: IntelliCageLearningCurveResult):
        self.report_view.set_content(result.report)
        self.curve_data = result.curve_data
        self.summary = result.summary

    def _finished(self):
        self.toast.hide()
        self.update_action.setEnabled(True)
        self.export_excel_action.setEnabled(self.curve_data is not None)

    def _export_to_excel(self) -> None:
        if self.curve_data is None or self.summary is None:
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Export to Excel", "", "Excel Files (*.xlsx)")
        if filename:
            with pd.ExcelWriter(filename) as writer:
                self.curve_data.to_excel(writer, sheet_name="Curve Data", index=False)
                self.summary.to_excel(writer, sheet_name="Summary", index=False)
