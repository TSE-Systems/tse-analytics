from typing import Literal

from PySide6 import QtCore
from PySide6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel, QSpinBox, QPushButton

from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import AnimalDataChangedMessage, BinningAppliedMessage


class BinningWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.binning_unit: Literal["day", "hour", "minute"] = "hour"
        self.binning_delta = 1
        self.binning_mode: Literal["sum", "mean", "median"] = "sum"

        layout = QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(layout)

        layout.addWidget(QLabel("Unit:"))
        self.unit_combobox = QComboBox()
        self.unit_combobox.addItems(["day", "hour", "minute"])
        self.unit_combobox.setCurrentText(self.binning_unit)
        self.unit_combobox.currentTextChanged.connect(self._binning_unit_changed)
        layout.addWidget(self.unit_combobox)

        layout.addWidget(QLabel("Delta:"))
        self.delta_spinbox = QSpinBox()
        self.delta_spinbox.setValue(self.binning_delta)
        self.delta_spinbox.valueChanged.connect(self._on_binning_delta_changed)
        layout.addWidget(self.delta_spinbox)

        layout.addWidget(QLabel("Mode:"))
        self.mode_combobox = QComboBox()
        self.mode_combobox.addItems(["sum", "mean", "median"])
        self.mode_combobox.setCurrentText(self.binning_mode)
        self.mode_combobox.currentTextChanged.connect(self._binning_mode_changed)
        layout.addWidget(self.mode_combobox)

        self.apply_binning = QPushButton("Apply")
        self.apply_binning.setEnabled(False)
        self.apply_binning.pressed.connect(self._on_apply_binning_pressed)
        layout.addWidget(self.apply_binning)

    def clear(self):
        self.apply_binning.setEnabled(False)

    def set_data(self, message: AnimalDataChangedMessage):
        self.apply_binning.setEnabled(True)

    @QtCore.Slot(str)
    def _binning_unit_changed(self, value: str):
        self.binning_unit = value

    @QtCore.Slot(int)
    def _on_binning_delta_changed(self, value: int):
        self.binning_delta = value

    @QtCore.Slot(str)
    def _binning_mode_changed(self, value: str):
        self.binning_mode = value

    @QtCore.Slot()
    def _on_apply_binning_pressed(self):
        Manager.messenger.broadcast(BinningAppliedMessage(self, self.binning_unit, self.binning_delta, self.binning_mode))
