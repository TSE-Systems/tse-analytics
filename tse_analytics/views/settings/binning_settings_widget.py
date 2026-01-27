import pandas as pd
from PySide6.QtCore import QSize, QTime
from PySide6.QtWidgets import QHeaderView, QInputDialog, QWidget

from tse_analytics.core import messaging
from tse_analytics.core.data.binning import BinningMode
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import TimePhase
from tse_analytics.core.models.time_phases_model import TimePhasesModel
from tse_analytics.views.settings.binning_settings_widget_ui import Ui_BinningSettingsWidget


class BinningSettingsWidget(QWidget, messaging.MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_BinningSettingsWidget()
        self.ui.setupUi(self)

        self.dataset: Dataset | None = None

        messaging.subscribe(self, messaging.DatasetChangedMessage, self._on_dataset_changed)

        self.ui.groupBoxCycles.setVisible(False)
        self.ui.groupBoxPhases.setVisible(False)

        self.time_phases_model = TimePhasesModel(self.dataset)
        self.ui.tableViewTimePhases.setModel(self.time_phases_model)
        header = self.ui.tableViewTimePhases.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self.ui.binningModeComboBox.addItems(list(BinningMode))
        self.ui.binningModeComboBox.currentTextChanged.connect(self._binning_mode_changed)

        self.ui.unitComboBox.addItems(["day", "hour", "minute"])
        self.ui.unitComboBox.currentTextChanged.connect(self._binning_unit_changed)
        self.ui.deltaSpinBox.valueChanged.connect(self._binning_delta_changed)

        self.ui.timeEditLightCycleStart.editingFinished.connect(self._light_cycle_start_changed)
        self.ui.timeEditDarkCycleStart.editingFinished.connect(self._dark_cycle_start_changed)

        self.ui.toolButtonAddPhase.clicked.connect(self._add_time_phase)
        self.ui.toolButtonDeletePhase.clicked.connect(self._delete_time_phase)

        self.ui.applyBinningCheckBox.stateChanged.connect(self._apply_binning_changed)

    def _on_dataset_changed(self, message: messaging.DatasetChangedMessage):
        self.dataset = message.dataset
        self.time_phases_model.dataset = self.dataset
        if self.dataset is None:
            self.ui.applyBinningCheckBox.setChecked(False)
            self.ui.binningModeComboBox.setCurrentText(BinningMode.INTERVALS)

            self.time_phases_model.items = []
            # Trigger refresh.
            self.time_phases_model.layoutChanged.emit()
        else:
            self.ui.unitComboBox.setCurrentText(self.dataset.binning_settings.time_intervals_settings.unit)
            self.ui.deltaSpinBox.setValue(self.dataset.binning_settings.time_intervals_settings.delta)

            self.ui.timeEditLightCycleStart.setTime(
                QTime(self.dataset.binning_settings.time_cycles_settings.light_cycle_start)
            )
            self.ui.timeEditDarkCycleStart.setTime(
                QTime(self.dataset.binning_settings.time_cycles_settings.dark_cycle_start)
            )

            self.time_phases_model.items = self.dataset.binning_settings.time_phases_settings.time_phases
            # Trigger refresh.
            self.time_phases_model.layoutChanged.emit()

            self.ui.binningModeComboBox.setCurrentText(self.dataset.binning_settings.mode)
            self.ui.applyBinningCheckBox.setChecked(self.dataset.binning_settings.apply)

    def _binning_mode_changed(self, value: str):
        match value:
            case BinningMode.INTERVALS:
                self.ui.groupBoxIntervals.setVisible(True)
                self.ui.groupBoxCycles.setVisible(False)
                self.ui.groupBoxPhases.setVisible(False)
            case BinningMode.CYCLES:
                self.ui.groupBoxIntervals.setVisible(False)
                self.ui.groupBoxCycles.setVisible(True)
                self.ui.groupBoxPhases.setVisible(False)
            case BinningMode.PHASES:
                self.ui.groupBoxIntervals.setVisible(False)
                self.ui.groupBoxCycles.setVisible(False)
                self.ui.groupBoxPhases.setVisible(True)

        if self.dataset is not None:
            self.dataset.binning_settings.mode = BinningMode(self.ui.binningModeComboBox.currentText())
            self.dataset.apply_binning(self.dataset.binning_settings)

    def _apply_binning_changed(self, value: int):
        if self.dataset is not None:
            self.dataset.binning_settings.apply = self.ui.applyBinningCheckBox.isChecked()
            self.dataset.apply_binning(self.dataset.binning_settings)

    def _binning_unit_changed(self, value: str):
        if self.dataset is None:
            return
        self.dataset.binning_settings.time_intervals_settings.unit = value
        self.dataset.apply_binning(self.dataset.binning_settings)

    def _binning_delta_changed(self, value: int):
        if self.dataset is None:
            return
        self.dataset.binning_settings.time_intervals_settings.delta = value
        self.dataset.apply_binning(self.dataset.binning_settings)

    def _light_cycle_start_changed(self):
        if self.dataset is None:
            return
        self.dataset.binning_settings.time_cycles_settings.light_cycle_start = (
            self.ui.timeEditLightCycleStart.time().toPython()
        )
        self.dataset.apply_binning(self.dataset.binning_settings)

    def _dark_cycle_start_changed(self):
        if self.dataset is None:
            return
        self.dataset.binning_settings.time_cycles_settings.dark_cycle_start = (
            self.ui.timeEditDarkCycleStart.time().toPython()
        )
        self.dataset.apply_binning(self.dataset.binning_settings)

    def _add_time_phase(self):
        if self.dataset is None:
            return
        text, result = QInputDialog.getText(self, "Add Time Phase", "Please enter unique phase name:")
        if result:
            start_timestamp = pd.Timedelta("0 days 00:00:00")
            if len(self.time_phases_model.items) > 0:
                start_timestamp = self.time_phases_model.items[-1].start_timestamp
                start_timestamp = start_timestamp + pd.to_timedelta(1, unit="hours")
            time_phase = TimePhase(name=text, start_timestamp=start_timestamp)
            self.time_phases_model.add_time_phase(time_phase)
            self.dataset.apply_binning(self.dataset.binning_settings)

    def _delete_time_phase(self):
        if self.dataset is None:
            return
        indexes = self.ui.tableViewTimePhases.selectedIndexes()
        if indexes:
            # Indexes is a single-item list in single-select mode.
            index = indexes[0]
            self.time_phases_model.delete_time_phase(index)
            # Clear the selection (as it is no longer valid).
            self.ui.tableViewTimePhases.clearSelection()
            self.dataset.apply_binning(self.dataset.binning_settings)

    def minimumSizeHint(self):
        return QSize(300, 70)
