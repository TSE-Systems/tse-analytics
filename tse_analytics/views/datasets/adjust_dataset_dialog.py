import pandas as pd
from PySide6.QtCore import QTime
from PySide6.QtWidgets import QDialog, QTableWidgetItem, QWidget

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.views.datasets.adjust_dataset_dialog_ui import Ui_AdjustDatasetDialog


class AdjustDatasetDialog(QDialog):
    def __init__(self, dataset: Dataset, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_AdjustDatasetDialog()
        self.ui.setupUi(self)

        self.dataset = dataset

        self.ui.buttonBox.accepted.connect(self._accepted)

        self.ui.lineEditName.setText(dataset.name)

        if "Main" in dataset.datatables and dataset.datatables["Main"].sampling_interval is not None:
            resampling_interval = dataset.datatables["Main"].sampling_interval
        else:
            resampling_interval = pd.to_timedelta("0 days 01:00:00")
        resampling_qtime = QTime.fromMSecsSinceStartOfDay(int(resampling_interval.total_seconds() * 1000))
        self.ui.timeEditResamplingInterval.setTime(resampling_qtime)
        self.ui.timeEditResamplingInterval.setMinimumTime(resampling_qtime)

        self.ui.dateTimeEditTrimStart.setMinimumDateTime(dataset.experiment_started)
        self.ui.dateTimeEditTrimStart.setMaximumDateTime(dataset.experiment_stopped)
        self.ui.dateTimeEditTrimStart.setDateTime(dataset.experiment_started)

        self.ui.dateTimeEditTrimEnd.setMinimumDateTime(dataset.experiment_started)
        self.ui.dateTimeEditTrimEnd.setMaximumDateTime(dataset.experiment_stopped)
        self.ui.dateTimeEditTrimEnd.setDateTime(dataset.experiment_stopped)

        self.ui.dateTimeEditExcludeStart.setMinimumDateTime(dataset.experiment_started)
        self.ui.dateTimeEditExcludeStart.setMaximumDateTime(dataset.experiment_stopped)
        self.ui.dateTimeEditExcludeStart.setDateTime(dataset.experiment_started)

        self.ui.dateTimeEditExcludeEnd.setMinimumDateTime(dataset.experiment_started)
        self.ui.dateTimeEditExcludeEnd.setMaximumDateTime(dataset.experiment_stopped)
        self.ui.dateTimeEditExcludeEnd.setDateTime(dataset.experiment_stopped)

        self.ui.tableWidgetAnimals.setHorizontalHeaderLabels(["Animal"])
        self.ui.tableWidgetAnimals.setRowCount(len(self.dataset.animals))
        for i, animal in enumerate(self.dataset.animals.values()):
            if i == 0:
                self.ui.tableWidgetAnimals.setColumnCount(len(animal.properties) + 1)
                self.ui.tableWidgetAnimals.setHorizontalHeaderLabels(["Animal"] + list(animal.properties.keys()))
            self.ui.tableWidgetAnimals.setItem(i, 0, QTableWidgetItem(animal.id))
            for j, item in enumerate(animal.properties):
                self.ui.tableWidgetAnimals.setItem(i, j + 1, QTableWidgetItem(str(animal.properties[item])))

    def _rename(self) -> None:
        name = self.ui.lineEditName.text()
        self.dataset.rename(name)

    def _resample(self) -> None:
        resampling_interval = pd.to_timedelta(
            self.ui.timeEditResamplingInterval.time().msecsSinceStartOfDay(), unit="ms"
        )
        self.dataset.resample(resampling_interval)

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

        if self.ui.groupBoxTrimTime.isChecked():
            self._trim_time()

        if self.ui.groupBoxExcludeTime.isChecked():
            self._exclude_time()

        if self.ui.groupBoxExcludeAnimals.isChecked():
            self._exclude_animals()
