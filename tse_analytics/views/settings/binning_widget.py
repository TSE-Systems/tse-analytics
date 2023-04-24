from typing import Optional

import pandas as pd
from PySide6 import QtCore
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QLabel,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QGroupBox,
    QScrollArea,
)

from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import BinningAppliedMessage, RevertBinningMessage
from tse_datatools.analysis.binning_operation import BinningOperation
from tse_datatools.analysis.binning_params import BinningParams
from tse_datatools.analysis.grouping_mode import GroupingMode


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
        grouping_mode_combo_box.currentTextChanged.connect(self.__grouping_mode_changed)
        layout.addWidget(grouping_mode_combo_box)

        binning_groupbox = QGroupBox("Binning")
        binning_layout = QVBoxLayout()

        self.apply_binning_checkbox = QCheckBox("Apply")
        self.apply_binning_checkbox.stateChanged.connect(self.__apply_binning_changed)
        binning_layout.addWidget(self.apply_binning_checkbox)

        binning_layout.addWidget(QLabel("Unit:"))
        self.unit_combobox = QComboBox()
        self.unit_combobox.addItems(["day", "hour", "minute"])
        self.unit_combobox.setCurrentText("hour")
        self.unit_combobox.currentTextChanged.connect(self.__binning_unit_changed)
        binning_layout.addWidget(self.unit_combobox)

        binning_layout.addWidget(QLabel("Delta:"))
        self.delta_spinbox = QSpinBox()
        self.delta_spinbox.setValue(1)
        self.delta_spinbox.valueChanged.connect(self.__binning_delta_changed)
        binning_layout.addWidget(self.delta_spinbox)

        binning_layout.addWidget(QLabel("Operation:"))
        self.operation_combobox = QComboBox()
        self.operation_combobox.addItems([e.value for e in BinningOperation])
        self.operation_combobox.setCurrentText("mean")
        self.operation_combobox.currentTextChanged.connect(self.__binning_operation_changed)
        binning_layout.addWidget(self.operation_combobox)

        binning_groupbox.setLayout(binning_layout)
        layout.addWidget(binning_groupbox)

        self.setWidget(widget)

    @QtCore.Slot(str)
    def __binning_unit_changed(self, value: str):
        self.__binning_params_changed()

    @QtCore.Slot(int)
    def __binning_delta_changed(self, value: int):
        self.__binning_params_changed()

    @QtCore.Slot(str)
    def __binning_operation_changed(self, value: str):
        self.__binning_params_changed()

    @QtCore.Slot(int)
    def __apply_binning_changed(self, value: int):
        Manager.data.binning_params.apply = value == 2
        if Manager.data.selected_dataset is not None:
            if Manager.data.binning_params.apply:
                Manager.messenger.broadcast(BinningAppliedMessage(self, Manager.data.binning_params))
            else:
                Manager.messenger.broadcast(RevertBinningMessage(self))

    @QtCore.Slot(str)
    def __grouping_mode_changed(self, text: str):
        Manager.data.set_grouping_mode(GroupingMode(text))

    def __binning_params_changed(self):
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

    def minimumSizeHint(self):
        return QSize(200, 40)
