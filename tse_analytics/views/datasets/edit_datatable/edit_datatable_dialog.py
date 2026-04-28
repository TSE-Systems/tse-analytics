from PySide6.QtWidgets import QDialog, QTableWidgetItem, QWidget

from tse_analytics.core import manager, messaging
from tse_analytics.core.data.binning import (
    TimeIntervalsBinningSettings,
)
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.services.action_log_service import record_create_derived_datatable
from tse_analytics.views.datasets.edit_datatable.edit_datatable_dialog_ui import Ui_EditDatatableDialog
from tse_analytics.views.datasets.edit_datatable.processor import process_table


class EditDatatableDialog(QDialog):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_EditDatatableDialog()
        self.ui.setupUi(self)

        self.datatable = datatable

        self.ui.buttonBox.accepted.connect(self._accepted)

        self.ui.nameLineEdit.setText(self.datatable.name)
        self.ui.descriptionLineEdit.setText(self.datatable.description)

        self.ui.unitComboBox.addItems(["day", "hour", "minute"])

        self.ui.unitComboBox.setCurrentText("hour")
        self.ui.deltaSpinBox.setValue(1)

        # Exclude Animals
        self.ui.tableWidgetAnimals.setHorizontalHeaderLabels(["Animal"])
        self.ui.tableWidgetAnimals.setRowCount(len(self.datatable.dataset.animals))
        for i, animal in enumerate(self.datatable.dataset.animals.values()):
            if i == 0:
                self.ui.tableWidgetAnimals.setColumnCount(len(animal.properties) + 1)
                self.ui.tableWidgetAnimals.setHorizontalHeaderLabels(["Animal"] + list(animal.properties.keys()))
            self.ui.tableWidgetAnimals.setItem(i, 0, QTableWidgetItem(animal.id))
            for j, item in enumerate(animal.properties):
                self.ui.tableWidgetAnimals.setItem(i, j + 1, QTableWidgetItem(str(animal.properties[item])))
        self.ui.tableWidgetAnimals.resizeColumnsToContents()

    def _accepted(self) -> None:
        datatable = Datatable(
            dataset=self.datatable.dataset,
            name=self.ui.nameLineEdit.text(),
            description=self.ui.descriptionLineEdit.text(),
            variables=self.datatable.variables.copy(),
            df=self.datatable.df.copy(),
            metadata=self.datatable.metadata.copy(),
        )

        selected_indices = self.ui.tableWidgetAnimals.selectionModel().selectedRows()
        excluded_animal_ids = set()
        for index in selected_indices:
            excluded_animal_ids.add(self.ui.tableWidgetAnimals.item(index.row(), 0).text())

        binning = (
            TimeIntervalsBinningSettings(
                unit=self.ui.unitComboBox.currentText(),
                delta=self.ui.deltaSpinBox.value(),
            )
            if self.ui.groupBoxResampling.isChecked()
            else None
        )

        process_table(
            datatable,
            excluded_animal_ids,
            binning,
        )

        self.datatable.dataset.add_datatable(datatable)

        record_create_derived_datatable(
            self,
            self.datatable.dataset,
            source_datatable_name=self.datatable.name,
            target_datatable_name=datatable.name,
            target_description=datatable.description,
            excluded_animal_ids=excluded_animal_ids,
            binning=binning,
        )

        # Notify that the table has been edited.
        workspace = manager.get_workspace()
        messaging.broadcast(messaging.WorkspaceChangedMessage(self, workspace))
