import pandas as pd
from PySide6.QtWidgets import QDialog, QTableWidgetItem, QWidget

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.services.action_log_service import (
    record_exclude_animals,
    record_exclude_time,
    record_trim_time,
)
from tse_analytics.views.datasets.edit_dataset.edit_dataset_dialog_ui import Ui_EditDatasetDialog

"""
Edit dataset dialog module for TSE Analytics.

This module provides a dialog for adjusting various properties of a dataset,
including renaming, resampling, trimming time, excluding time periods, and excluding animals.
"""


class EditDatasetDialog(QDialog):
    """
    Dialog for adjusting dataset properties.

    This dialog allows users to modify various aspects of a dataset, including:
    - Renaming the dataset
    - Resampling the data at a different time interval
    - Trimming the dataset to a specific time range
    - Excluding specific time periods
    - Excluding specific animals
    """

    def __init__(self, dataset: Dataset, parent: QWidget | None = None):
        """
        Initialize the AdjustDatasetDialog with a dataset and optional parent widget.

        Args:
            dataset (Dataset): The dataset to adjust
            parent (QWidget | None, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.ui = Ui_EditDatasetDialog()
        self.ui.setupUi(self)

        self.dataset = dataset

        self.ui.buttonBox.accepted.connect(self._accepted)

        self.ui.lineEditName.setText(dataset.name)

        self.ui.comboBoxResamplingUnit.addItems(["day", "hour", "minute"])
        self.ui.comboBoxResamplingUnit.setCurrentIndex(1)

        # self.ui.dateTimeEditTrimStart.setMinimumDateTime(dataset.experiment_started.to_pydatetime())
        # self.ui.dateTimeEditTrimStart.setMaximumDateTime(dataset.experiment_stopped.to_pydatetime())
        self.ui.dateTimeEditTrimStart.setDateTime(dataset.experiment_started.to_pydatetime())

        # self.ui.dateTimeEditTrimEnd.setMinimumDateTime(dataset.experiment_started.to_pydatetime())
        # self.ui.dateTimeEditTrimEnd.setMaximumDateTime(dataset.experiment_stopped.to_pydatetime())
        self.ui.dateTimeEditTrimEnd.setDateTime(dataset.experiment_stopped.to_pydatetime())

        # self.ui.dateTimeEditExcludeStart.setMinimumDateTime(dataset.experiment_started.to_pydatetime())
        # self.ui.dateTimeEditExcludeStart.setMaximumDateTime(dataset.experiment_stopped.to_pydatetime())
        self.ui.dateTimeEditExcludeStart.setDateTime(dataset.experiment_started.to_pydatetime())

        # self.ui.dateTimeEditExcludeEnd.setMinimumDateTime(dataset.experiment_started.to_pydatetime())
        # self.ui.dateTimeEditExcludeEnd.setMaximumDateTime(dataset.experiment_stopped.to_pydatetime())
        self.ui.dateTimeEditExcludeEnd.setDateTime(dataset.experiment_stopped.to_pydatetime())

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
        """
        Rename the dataset with the name entered in the line edit.
        """
        name = self.ui.lineEditName.text()
        self.dataset.rename(name)

    def _resample(self) -> None:
        value = self.ui.spinBoxResamplingValue.value()
        unit = self.ui.comboBoxResamplingUnit.currentText()
        resample_interval = pd.Timedelta(f"{value}{unit}")
        self.dataset.resample(resample_interval)

    def _trim_time(self) -> None:
        """
        Trim the dataset to the time range specified in the date time edits.
        """
        start = self.ui.dateTimeEditTrimStart.dateTime().toPython()
        end = self.ui.dateTimeEditTrimEnd.dateTime().toPython()
        self.dataset.trim_time(start, end)
        record_trim_time(self, self.dataset, start, end)

    def _exclude_time(self) -> None:
        """
        Exclude the time range specified in the date time edits from the dataset.
        """
        start = self.ui.dateTimeEditExcludeStart.dateTime().toPython()
        end = self.ui.dateTimeEditExcludeEnd.dateTime().toPython()
        self.dataset.exclude_time(start, end)
        record_exclude_time(self, self.dataset, start, end)

    def _exclude_animals(self) -> None:
        """
        Exclude the selected animals from the dataset.
        """
        selected_indices = self.ui.tableWidgetAnimals.selectionModel().selectedRows()
        selected_animal_ids = set()
        for index in selected_indices:
            selected_animal_ids.add(self.ui.tableWidgetAnimals.item(index.row(), 0).text())
        self.dataset.exclude_animals(selected_animal_ids)
        if selected_animal_ids:
            record_exclude_animals(self, self.dataset, selected_animal_ids)

    def _accepted(self) -> None:
        """
        Handle the accepted signal from the dialog.

        Applies the selected adjustments to the dataset based on which group boxes are checked.
        """
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
