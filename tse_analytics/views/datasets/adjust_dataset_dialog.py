import pandas as pd
from PySide6.QtCore import QTime
from PySide6.QtWidgets import QDialog, QWidget

from tse_analytics.modules.phenomaster.data.dataset import Dataset
from tse_analytics.views.datasets.adjust_dataset_dialog_ui import Ui_AdjustDatasetDialog


class AdjustDatasetDialog(QDialog):
    def __init__(self, dataset: Dataset, resampling_interval: pd.Timedelta, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_AdjustDatasetDialog()
        self.ui.setupUi(self)

        self.ui.buttonBox.accepted.connect(self._accepted)

        self.dataset = dataset

        self.setWindowTitle(f"Dataset: {dataset.name}")
        resampling_qtime = QTime.fromMSecsSinceStartOfDay(int(resampling_interval.total_seconds() * 1000))
        self.ui.timeEditResamplingInterval.setTime(resampling_qtime)
        self.ui.timeEditResamplingInterval.setMinimumTime(resampling_qtime)

        self.ui.dateTimeEditStart.setMinimumDateTime(dataset.start_timestamp)
        self.ui.dateTimeEditStart.setMaximumDateTime(dataset.end_timestamp)
        self.ui.dateTimeEditStart.setDateTime(dataset.start_timestamp)

        self.ui.dateTimeEditEnd.setMinimumDateTime(dataset.start_timestamp)
        self.ui.dateTimeEditEnd.setMaximumDateTime(dataset.end_timestamp)
        self.ui.dateTimeEditEnd.setDateTime(dataset.end_timestamp)

    def _resample(self):
        resampling_interval = pd.to_timedelta(
            self.ui.timeEditResamplingInterval.time().msecsSinceStartOfDay(), unit="ms"
        )
        self.dataset.resample(resampling_interval)

    def _shift_time(self):
        delta = pd.to_timedelta(self.ui.spinBoxTimeShiftDays.value(), unit="d") + pd.to_timedelta(
            self.ui.timeEditTimeShift.time().msecsSinceStartOfDay(), unit="ms"
        )
        if self.ui.radioButtonTimeShiftMinus.isChecked():
            delta = -delta
        self.dataset.adjust_time(delta)

    def _trim_time(self):
        start = self.ui.dateTimeEditStart.dateTime().toPython()
        end = self.ui.dateTimeEditEnd.dateTime().toPython()
        self.dataset.trim_time(start, end)

    def _accepted(self):
        if self.ui.groupBoxTrimTime.isChecked():
            self._trim_time()

        if self.ui.groupBoxTimeShift.isChecked():
            self._shift_time()

        if self.ui.groupBoxResampling.isChecked():
            self._resample()
