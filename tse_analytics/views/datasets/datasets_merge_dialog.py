from copy import deepcopy
from functools import partial

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHeaderView,
    QPushButton,
    QTableWidgetItem,
    QWidget,
)

from tse_analytics.core.manager import Manager
from tse_analytics.modules.phenomaster.data.dataset import Dataset
from tse_analytics.views.datasets.adjust_dataset_dialog import AdjustDatasetDialog
from tse_analytics.views.datasets.datasets_merge_dialog_ui import Ui_DatasetsMergeDialog


class DatasetsMergeDialog(QDialog):
    def __init__(self, datasets: list[Dataset], parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_DatasetsMergeDialog()
        self.ui.setupUi(self)

        self.ui.buttonBox.accepted.connect(self._accepted)

        self.ui.radioButtonOverlapMode.toggled.connect(
            lambda toggled: self.ui.checkBoxGenerateAnimalNames.setEnabled(True) if toggled else None
        )

        self.ui.radioButtonContinuousMode.toggled.connect(
            lambda toggled: self.ui.checkBoxGenerateAnimalNames.setEnabled(False) if toggled else None
        )

        self.datasets = deepcopy(datasets)

        # sort datasets by start time
        self.datasets.sort(key=lambda x: x.start_timestamp)

        header_labels = ["Name", "Start", "End", "Duration", "Sampling Interval", ""]
        self.ui.tableWidget.setColumnCount(len(header_labels))
        self.ui.tableWidget.setHorizontalHeaderLabels(header_labels)
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.ui.tableWidget.setRowCount(len(self.datasets))

        self._update_table()
        self.ui.tableWidget.resizeColumnsToContents()

        self.ui.lineEditName.setText(f"{self.datasets[0].name} (merged)")

    def _update_table(self):
        for i, dataset in enumerate(self.datasets):
            self.ui.tableWidget.setItem(i, 0, QTableWidgetItem(dataset.name))
            self.ui.tableWidget.setItem(i, 1, QTableWidgetItem(str(dataset.start_timestamp)))
            self.ui.tableWidget.setItem(i, 2, QTableWidgetItem(str(dataset.end_timestamp)))
            self.ui.tableWidget.setItem(i, 3, QTableWidgetItem(str(dataset.duration)))
            self.ui.tableWidget.setItem(i, 4, QTableWidgetItem(str(dataset.sampling_interval)))

            adjust_button = QPushButton("Adjust...")
            adjust_button.clicked.connect(partial(self._adjust_dataset, dataset))
            self.ui.tableWidget.setCellWidget(i, 5, adjust_button)

    def _adjust_dataset(self, dataset: Dataset):
        max_sampling_interval = max(dataset.sampling_interval for dataset in self.datasets)
        dialog = AdjustDatasetDialog(dataset, max_sampling_interval, self)
        # TODO: check other cases!!
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._update_table()

    def _accepted(self):
        new_dataset_name = self.ui.lineEditName.text()
        single_run = self.ui.checkBoxSingleRun.isChecked()
        continuous_mode = self.ui.radioButtonContinuousMode.isChecked()
        generate_new_animal_names = self.ui.checkBoxGenerateAnimalNames.isChecked()
        Manager.merge_datasets(new_dataset_name, self.datasets, single_run, continuous_mode, generate_new_animal_names)
