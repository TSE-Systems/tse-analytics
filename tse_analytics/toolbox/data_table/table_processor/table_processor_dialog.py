import pandas as pd
from PySide6.QtCore import QTime
from PySide6.QtWidgets import QDialog, QHeaderView, QInputDialog, QTableWidgetItem, QWidget

from tse_analytics.core import manager, messaging
from tse_analytics.core.data.binning import (
    BinningMode,
    BinningSettings,
    TimeCyclesBinningSettings,
    TimeIntervalsBinningSettings,
)
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.grouping import GroupingMode, GroupingSettings
from tse_analytics.core.data.shared import TimePhase
from tse_analytics.core.models.time_phases_model import TimePhasesModel
from tse_analytics.toolbox.data_table.table_processor.processor import process_derived_table
from tse_analytics.toolbox.data_table.table_processor.table_processor_dialog_ui import Ui_TableProcessorDialog


class TableProcessorDialog(QDialog):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_TableProcessorDialog()
        self.ui.setupUi(self)

        self.datatable = datatable

        self.ui.buttonBox.accepted.connect(self._accepted)

        self.ui.nameLineEdit.setText(f"{self.datatable.name} (derived)")
        self.ui.descriptionLineEdit.setText(self.datatable.description)

        self.ui.widgetCycles.setVisible(False)
        self.ui.widgetPhases.setVisible(False)

        self.ui.binningModeComboBox.addItems(list(BinningMode))
        self.ui.binningModeComboBox.currentTextChanged.connect(self._binning_mode_changed)

        self.ui.unitComboBox.addItems(["day", "hour", "minute"])

        self.ui.toolButtonAddPhase.clicked.connect(self._add_time_phase)
        self.ui.toolButtonDeletePhase.clicked.connect(self._delete_time_phase)

        self.ui.unitComboBox.setCurrentText(self.datatable.dataset.binning_settings.time_intervals_settings.unit)
        self.ui.deltaSpinBox.setValue(self.datatable.dataset.binning_settings.time_intervals_settings.delta)

        self.ui.timeEditLightCycleStart.setTime(
            QTime(self.datatable.dataset.binning_settings.time_cycles_settings.light_cycle_start)
        )
        self.ui.timeEditDarkCycleStart.setTime(
            QTime(self.datatable.dataset.binning_settings.time_cycles_settings.dark_cycle_start)
        )

        self.time_phases_model = TimePhasesModel(self.datatable.dataset)
        self.ui.tableViewTimePhases.setModel(self.time_phases_model)
        header = self.ui.tableViewTimePhases.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self.time_phases_model.items = self.datatable.dataset.binning_settings.time_phases_settings.time_phases
        # Trigger refresh.
        self.time_phases_model.layoutChanged.emit()

        self.ui.binningModeComboBox.setCurrentText(self.datatable.dataset.binning_settings.mode)

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

        # Grouping
        modes = self.datatable.get_group_by_columns(True, False)
        self.ui.comboBoxGrouping.addItems(modes)

    def _binning_mode_changed(self, value: str):
        match value:
            case BinningMode.INTERVALS:
                self.ui.widgetIntervals.setVisible(True)
                self.ui.widgetCycles.setVisible(False)
                self.ui.widgetPhases.setVisible(False)
            case BinningMode.CYCLES:
                self.ui.widgetIntervals.setVisible(False)
                self.ui.widgetCycles.setVisible(True)
                self.ui.widgetPhases.setVisible(False)
            case BinningMode.PHASES:
                self.ui.widgetIntervals.setVisible(False)
                self.ui.widgetCycles.setVisible(False)
                self.ui.widgetPhases.setVisible(True)

    def _add_time_phase(self):
        text, result = QInputDialog.getText(self, "Add Time Phase", "Please enter unique phase name:")
        if result:
            start_timestamp = pd.Timedelta("0 days 00:00:00")
            if len(self.time_phases_model.items) > 0:
                start_timestamp = self.time_phases_model.items[-1].start_timestamp
                start_timestamp = start_timestamp + pd.to_timedelta(1, unit="hours")
            time_phase = TimePhase(name=text, start_timestamp=start_timestamp)
            self.time_phases_model.add_time_phase(time_phase)

    def _delete_time_phase(self):
        indexes = self.ui.tableViewTimePhases.selectedIndexes()
        if indexes:
            # Indexes is a single-item list in single-select mode.
            index = indexes[0]
            self.time_phases_model.delete_time_phase(index)
            # Clear the selection (as it is no longer valid).
            self.ui.tableViewTimePhases.clearSelection()

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

        binning_settings = BinningSettings(
            apply=self.ui.groupBoxBinning.isChecked(),
            mode=BinningMode(self.ui.binningModeComboBox.currentText()),
            time_intervals_settings=TimeIntervalsBinningSettings(
                unit=self.ui.unitComboBox.currentText(),
                delta=self.ui.deltaSpinBox.value(),
            ),
            time_cycles_settings=TimeCyclesBinningSettings(
                light_cycle_start=self.ui.timeEditLightCycleStart.time().toPython(),
                dark_cycle_start=self.ui.timeEditDarkCycleStart.time().toPython(),
            ),
            time_phases_settings=self.datatable.dataset.binning_settings.time_phases_settings,
        )
        self.datatable.dataset.binning_settings = binning_settings

        grouping_mode_text = self.ui.comboBoxGrouping.currentText()
        factor_name = ""
        match grouping_mode_text:
            case "Animal":
                grouping_mode = GroupingMode.ANIMAL
            case "Total":
                grouping_mode = GroupingMode.TOTAL
            case "Run":
                grouping_mode = GroupingMode.RUN
            case _:
                grouping_mode = GroupingMode.FACTOR
                factor_name = grouping_mode_text

        grouping_settings = GroupingSettings(
            mode=grouping_mode,
            factor_name=factor_name,
        )

        process_derived_table(
            datatable,
            excluded_animal_ids,
            binning_settings,
            grouping_settings,
        )

        self.datatable.derived_tables[datatable.id] = datatable

        # Notify that a derived table has been added.
        workspace = manager.get_workspace()
        messaging.broadcast(messaging.WorkspaceChangedMessage(self, workspace))
