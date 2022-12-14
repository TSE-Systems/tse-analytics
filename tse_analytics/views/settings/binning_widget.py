from typing import Optional

import pandas as pd
from PySide6 import QtCore
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import BinningAppliedMessage, RevertBinningMessage
from tse_datatools.analysis.binning_operation import BinningOperation
from tse_datatools.analysis.binning_params import BinningParams
from tse_datatools.analysis.grouping_mode import GroupingMode


class BinningWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(QLabel("Unit:"))
        self.unit_combobox = QComboBox()
        self.unit_combobox.addItems(["day", "hour", "minute"])
        self.unit_combobox.setCurrentText("hour")
        self.unit_combobox.currentTextChanged.connect(self._binning_unit_changed)
        layout.addWidget(self.unit_combobox)

        layout.addWidget(QLabel("Delta:"))
        self.delta_spinbox = QSpinBox()
        self.delta_spinbox.setValue(1)
        self.delta_spinbox.valueChanged.connect(self._binning_delta_changed)
        layout.addWidget(self.delta_spinbox)

        self.apply_binning_checkbox = QCheckBox("Apply Binning")
        self.apply_binning_checkbox.stateChanged.connect(self._apply_binning_changed)
        layout.addWidget(self.apply_binning_checkbox)

        layout.addWidget(QLabel("Operation:"))
        self.operation_combobox = QComboBox()
        self.operation_combobox.addItems([e.value for e in BinningOperation])
        self.operation_combobox.setCurrentText("mean")
        self.operation_combobox.currentTextChanged.connect(self._binning_operation_changed)
        layout.addWidget(self.operation_combobox)

        apply_binning_button = QPushButton("Apply")
        apply_binning_button.pressed.connect(self._apply_binning_pressed)
        layout.addWidget(apply_binning_button)

        layout.addWidget(QLabel("Grouping Mode: "))

        grouping_mode_combo_box = QComboBox()
        grouping_mode_combo_box.addItems([e.value for e in GroupingMode])
        grouping_mode_combo_box.currentTextChanged.connect(self._grouping_mode_changed)
        layout.addWidget(grouping_mode_combo_box)

        revert_binning_button = QPushButton("Revert to Original Data")
        revert_binning_button.pressed.connect(self._revert_binning_pressed)
        layout.addWidget(revert_binning_button)

        self.setLayout(layout)

    @QtCore.Slot(str)
    def _binning_unit_changed(self, value: str):
        self._binning_params_changed()

    @QtCore.Slot(int)
    def _binning_delta_changed(self, value: int):
        self._binning_params_changed()

    @QtCore.Slot(str)
    def _binning_operation_changed(self, value: str):
        self._binning_params_changed()

    @QtCore.Slot(bool)
    def _apply_binning_changed(self, value: int):
        Manager.data.apply_binning = True if value == 2 else False

    @QtCore.Slot(str)
    def _grouping_mode_changed(self, text: str):
        Manager.data.set_grouping_mode(GroupingMode(text))

    @QtCore.Slot()
    def _apply_binning_pressed(self):
        if Manager.data.selected_dataset is not None:
            Manager.messenger.broadcast(BinningAppliedMessage(self, Manager.data.binning_params))

    @QtCore.Slot()
    def _revert_binning_pressed(self):
        if Manager.data.selected_dataset is not None:
            self.apply_binning_checkbox.setCheckState(Qt.CheckState.Unchecked)
            Manager.messenger.broadcast(RevertBinningMessage(self))

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

        binning_params = BinningParams(timedelta, BinningOperation(self.operation_combobox.currentText()))
        Manager.data.binning_params = binning_params

    def minimumSizeHint(self):
        return QSize(200, 40)
