import pandas as pd
from PySide6.QtCore import QTime
from PySide6.QtWidgets import QDialog, QWidget, QTableWidgetItem

from tse_analytics.modules.phenomaster.data.dataset import Dataset
from tse_analytics.views.datasets.adjust_dataset_dialog_ui import Ui_AdjustDatasetDialog


class AdjustDatasetDialog(QDialog):
    def __init__(self, dataset: Dataset, resampling_interval: pd.Timedelta, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_AdjustDatasetDialog()
        self.ui.setupUi(self)

        self.ui.buttonBox.accepted.connect(self._accepted)

        self.dataset = dataset

        self.ui.lineEditName.setText(dataset.name)

        resampling_qtime = QTime.fromMSecsSinceStartOfDay(int(resampling_interval.total_seconds() * 1000))
        self.ui.timeEditResamplingInterval.setTime(resampling_qtime)
        self.ui.timeEditResamplingInterval.setMinimumTime(resampling_qtime)

        self.ui.dateTimeEditTrimStart.setMinimumDateTime(dataset.start_timestamp)
        self.ui.dateTimeEditTrimStart.setMaximumDateTime(dataset.end_timestamp)
        self.ui.dateTimeEditTrimStart.setDateTime(dataset.start_timestamp)

        self.ui.dateTimeEditTrimEnd.setMinimumDateTime(dataset.start_timestamp)
        self.ui.dateTimeEditTrimEnd.setMaximumDateTime(dataset.end_timestamp)
        self.ui.dateTimeEditTrimEnd.setDateTime(dataset.end_timestamp)

        self.ui.dateTimeEditExcludeStart.setMinimumDateTime(dataset.start_timestamp)
        self.ui.dateTimeEditExcludeStart.setMaximumDateTime(dataset.end_timestamp)
        self.ui.dateTimeEditExcludeStart.setDateTime(dataset.start_timestamp)

        self.ui.dateTimeEditExcludeEnd.setMinimumDateTime(dataset.start_timestamp)
        self.ui.dateTimeEditExcludeEnd.setMaximumDateTime(dataset.end_timestamp)
        self.ui.dateTimeEditExcludeEnd.setDateTime(dataset.end_timestamp)

        self.ui.tableWidgetAnimals.setHorizontalHeaderLabels(["Animal", "Box", "Weight", "Text1", "Text2", "Text3"])
        self.ui.tableWidgetAnimals.setRowCount(len(self.dataset.animals))
        for i, animal in enumerate(self.dataset.animals.values()):
            self.ui.tableWidgetAnimals.setItem(i, 0, QTableWidgetItem(animal.id))
            self.ui.tableWidgetAnimals.setItem(i, 1, QTableWidgetItem(animal.box))
            self.ui.tableWidgetAnimals.setItem(i, 2, QTableWidgetItem(animal.weight))
            self.ui.tableWidgetAnimals.setItem(i, 3, QTableWidgetItem(animal.text1))
            self.ui.tableWidgetAnimals.setItem(i, 4, QTableWidgetItem(animal.text2))
            self.ui.tableWidgetAnimals.setItem(i, 5, QTableWidgetItem(animal.text3))

    def _rename(self) -> None:
        name = self.ui.lineEditName.text()
        self.dataset.name = name

    def _resample(self) -> None:
        resampling_interval = pd.to_timedelta(
            self.ui.timeEditResamplingInterval.time().msecsSinceStartOfDay(), unit="ms"
        )
        self.dataset.resample(resampling_interval)

    def _shift_time(self) -> None:
        delta = pd.to_timedelta(self.ui.spinBoxTimeShiftDays.value(), unit="d") + pd.to_timedelta(
            self.ui.timeEditTimeShift.time().msecsSinceStartOfDay(), unit="ms"
        )
        if self.ui.radioButtonTimeShiftMinus.isChecked():
            delta = -delta
        self.dataset.adjust_time(delta)

    def _trim_time(self) -> None:
        start = self.ui.dateTimeEditTrimStart.dateTime().toPython()
        end = self.ui.dateTimeEditTrimEnd.dateTime().toPython()
        self.dataset.trim_time(start, end)

    def _exclude_time(self) -> None:
        start = self.ui.dateTimeEditExcludeStart.dateTime().toPython()
        end = self.ui.dateTimeEditExcludeEnd.dateTime().toPython()
        self.dataset.exclude_time(start, end)

    def _exclude_animals(self) -> None:
        selected_items = self.ui.tableWidgetAnimals.selectedItems()
        selected_animal_ids = set()
        for i in range(0, len(selected_items) // 6):
            selected_animal_ids.add(selected_items[i * 6].text())
        self.dataset.exclude_animals(selected_animal_ids)

    def _accepted(self) -> None:
        if self.ui.groupBoxRename.isChecked():
            self._rename()

        if self.ui.groupBoxResampling.isChecked():
            self._resample()

        if self.ui.groupBoxTimeShift.isChecked():
            self._shift_time()

        if self.ui.groupBoxTrimTime.isChecked():
            self._trim_time()

        if self.ui.groupBoxExcludeTime.isChecked():
            self._exclude_time()

        if self.ui.groupBoxExcludeAnimals.isChecked():
            self._exclude_animals()
