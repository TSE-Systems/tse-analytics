from typing import Optional

import pandas as pd
from PySide6 import QtCore
from PySide6.QtCore import QSize, Qt, QTime
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QLabel,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QTimeEdit,
    QGroupBox,
    QScrollArea,
)

from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import BinningAppliedMessage, RevertBinningMessage
from tse_datatools.analysis.binning_operation import BinningOperation
from tse_datatools.analysis.binning_params import BinningParams
from tse_datatools.analysis.grouping_mode import GroupingMode
from tse_datatools.analysis.time_cycles_params import TimeCyclesParams


class BinningWidget(QScrollArea):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.setWidgetResizable(True)

        widget = QWidget(self)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        widget.setLayout(layout)

        layout.addWidget(QLabel("Grouping Mode: "))
        grouping_mode_combo_box = QComboBox()
        grouping_mode_combo_box.addItems([e.value for e in GroupingMode])
        grouping_mode_combo_box.currentTextChanged.connect(self._grouping_mode_changed)
        layout.addWidget(grouping_mode_combo_box)

        binning_groupbox = QGroupBox("Binning")
        binning_layout = QVBoxLayout()

        self.apply_binning_checkbox = QCheckBox("Apply")
        self.apply_binning_checkbox.stateChanged.connect(self._apply_binning_changed)
        binning_layout.addWidget(self.apply_binning_checkbox)

        binning_layout.addWidget(QLabel("Unit:"))
        self.unit_combobox = QComboBox()
        self.unit_combobox.addItems(["day", "hour", "minute"])
        self.unit_combobox.setCurrentText("hour")
        self.unit_combobox.currentTextChanged.connect(self._binning_unit_changed)
        binning_layout.addWidget(self.unit_combobox)

        binning_layout.addWidget(QLabel("Delta:"))
        self.delta_spinbox = QSpinBox()
        self.delta_spinbox.setValue(1)
        self.delta_spinbox.valueChanged.connect(self._binning_delta_changed)
        binning_layout.addWidget(self.delta_spinbox)

        binning_layout.addWidget(QLabel("Operation:"))
        self.operation_combobox = QComboBox()
        self.operation_combobox.addItems([e.value for e in BinningOperation])
        self.operation_combobox.setCurrentText("mean")
        self.operation_combobox.currentTextChanged.connect(self._binning_operation_changed)
        binning_layout.addWidget(self.operation_combobox)

        binning_groupbox.setLayout(binning_layout)
        layout.addWidget(binning_groupbox)

        time_cycles_groupbox = QGroupBox("Light/Dark Cycles")
        time_cycles_layout = QVBoxLayout()

        self.apply_time_cycles_checkbox = QCheckBox("Apply")
        self.apply_time_cycles_checkbox.stateChanged.connect(self._apply_time_cycles_changed)
        time_cycles_layout.addWidget(self.apply_time_cycles_checkbox)

        time_cycles_layout.addWidget(QLabel("Light cycle starts:"))
        self.light_cycle_start_edit = QTimeEdit()
        self.light_cycle_start_edit.setTime(QTime(7, 0))
        self.light_cycle_start_edit.editingFinished.connect(self._light_cycle_start_changed)
        time_cycles_layout.addWidget(self.light_cycle_start_edit)

        time_cycles_layout.addWidget(QLabel("Dark cycle starts:"))
        self.dark_cycle_start_edit = QTimeEdit()
        self.dark_cycle_start_edit.setTime(QTime(19, 0))
        self.dark_cycle_start_edit.editingFinished.connect(self._dark_cycle_start_changed)
        time_cycles_layout.addWidget(self.dark_cycle_start_edit)

        time_cycles_groupbox.setLayout(time_cycles_layout)
        layout.addWidget(time_cycles_groupbox)

        self.setWidget(widget)

    @QtCore.Slot(str)
    def _binning_unit_changed(self, value: str):
        self._binning_params_changed()

    @QtCore.Slot(int)
    def _binning_delta_changed(self, value: int):
        self._binning_params_changed()

    @QtCore.Slot(str)
    def _binning_operation_changed(self, value: str):
        self._binning_params_changed()

    @QtCore.Slot(int)
    def _apply_binning_changed(self, value: int):
        Manager.data.binning_params.apply = value == 2
        if Manager.data.selected_dataset is not None:
            if Manager.data.binning_params.apply:
                Manager.messenger.broadcast(BinningAppliedMessage(self, Manager.data.binning_params))
            else:
                Manager.messenger.broadcast(RevertBinningMessage(self))

    @QtCore.Slot(str)
    def _grouping_mode_changed(self, text: str):
        Manager.data.set_grouping_mode(GroupingMode(text))

    def _binning_params_changed(self):
        unit = "H"
        unit_value = self.unit_combobox.currentText()
        if unit_value == "day":
            unit = "D"
        elif unit_value == "hour":
            unit = "H"
        elif unit_value == "minute":
            unit = "min"

        binning_delta = self.delta_spinbox.value()

        timedelta = pd.Timedelta(f"{binning_delta}{unit}")

        binning_params = BinningParams(
            self.apply_binning_checkbox.isChecked(), timedelta, BinningOperation(self.operation_combobox.currentText())
        )
        Manager.data.binning_params = binning_params

    @QtCore.Slot(int)
    def _apply_time_cycles_changed(self, value: int):
        self._time_cycles_params_changed()

    @QtCore.Slot()
    def _light_cycle_start_changed(self):
        self._time_cycles_params_changed()

    @QtCore.Slot()
    def _dark_cycle_start_changed(self):
        self._time_cycles_params_changed()

    def _time_cycles_params_changed(self):
        apply = self.apply_time_cycles_checkbox.isChecked()
        light_cycle_start = self.light_cycle_start_edit.time().toPython()
        dark_cycle_start = self.dark_cycle_start_edit.time().toPython()
        params = TimeCyclesParams(apply, light_cycle_start, dark_cycle_start)
        Manager.data.time_cycles_params = params

    def minimumSizeHint(self):
        return QSize(200, 40)
