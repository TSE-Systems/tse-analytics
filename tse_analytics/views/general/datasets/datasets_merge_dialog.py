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

from tse_analytics.core import manager
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.views.general.datasets.adjust_dataset_dialog import AdjustDatasetDialog
from tse_analytics.views.general.datasets.datasets_merge_dialog_ui import Ui_DatasetsMergeDialog


class DatasetsMergeDialog(QDialog):
    def __init__(self, datasets: list[Dataset], parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_DatasetsMergeDialog()
        self.ui.setupUi(self)

        self.datasets = deepcopy(datasets)
        # sort datasets by start time
        self.datasets.sort(key=lambda dataset: dataset.experiment_started)

        self.ui.buttonBox.accepted.connect(self._accepted)

        self.ui.radioButtonOverlapMode.toggled.connect(
            lambda toggled: self.ui.checkBoxGenerateAnimalNames.setEnabled(True) if toggled else None
        )

        self.ui.radioButtonContinuousMode.toggled.connect(
            lambda toggled: self.ui.checkBoxGenerateAnimalNames.setEnabled(False) if toggled else None
        )

        header_labels = ["Name", "Start", "End", "Duration", ""]
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
            self.ui.tableWidget.setItem(i, 1, QTableWidgetItem(str(dataset.experiment_started)))
            self.ui.tableWidget.setItem(i, 2, QTableWidgetItem(str(dataset.experiment_stopped)))
            self.ui.tableWidget.setItem(i, 3, QTableWidgetItem(str(dataset.experiment_duration)))

            adjust_button = QPushButton("Adjust...")
            adjust_button.clicked.connect(partial(self._adjust_dataset, dataset))
            self.ui.tableWidget.setCellWidget(i, 4, adjust_button)

    def _adjust_dataset(self, dataset: Dataset):
        dialog = AdjustDatasetDialog(dataset, self)
        # TODO: check other cases!!
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._update_table()

    def _accepted(self):
        new_dataset_name = self.ui.lineEditName.text()
        single_run = self.ui.checkBoxSingleRun.isChecked()
        continuous_mode = self.ui.radioButtonContinuousMode.isChecked()
        generate_new_animal_names = self.ui.checkBoxGenerateAnimalNames.isChecked()
        manager.merge_datasets(new_dataset_name, self.datasets, single_run, continuous_mode, generate_new_animal_names)
