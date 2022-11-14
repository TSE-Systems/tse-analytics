import pandas as pd
from PySide6 import QtCore
from PySide6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel, QSpinBox, QPushButton

from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import BinningAppliedMessage
from tse_datatools.analysis.binning_params import BinningParams


class BinningWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(layout)

        layout.addWidget(QLabel("Unit:"))
        self.unit_combobox = QComboBox()
        self.unit_combobox.addItems(["day", "hour", "minute"])
        self.unit_combobox.setCurrentText("hour")
        layout.addWidget(self.unit_combobox)

        layout.addWidget(QLabel("Delta:"))
        self.delta_spinbox = QSpinBox()
        self.delta_spinbox.setValue(1)
        layout.addWidget(self.delta_spinbox)

        layout.addWidget(QLabel("Operation:"))
        self.mode_combobox = QComboBox()
        self.mode_combobox.addItems(["sum", "mean", "median"])
        self.mode_combobox.setCurrentText('mean')
        layout.addWidget(self.mode_combobox)

        self.apply_binning = QPushButton("Apply")
        self.apply_binning.pressed.connect(self._on_apply_binning_pressed)
        layout.addWidget(self.apply_binning)

    @QtCore.Slot()
    def _on_apply_binning_pressed(self):
        unit = "H"
        unit_value = self.unit_combobox.currentText()
        if unit_value == "day":
            unit = "D"
        elif unit_value == "hour":
            unit = "H"
        elif unit_value == "minute":
            unit = "min"

        binning_delta = self.delta_spinbox.value()

        timedelta = pd.Timedelta(f'{binning_delta}{unit}')

        binning_params = BinningParams(timedelta, self.mode_combobox.currentText())
        Manager.data.binning_params = binning_params
        Manager.messenger.broadcast(BinningAppliedMessage(self, binning_params))
