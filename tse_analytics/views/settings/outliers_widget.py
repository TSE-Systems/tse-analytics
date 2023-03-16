from typing import Optional

from PySide6 import QtCore
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QLabel,
    QVBoxLayout,
    QWidget, QDoubleSpinBox, QScrollArea,
)

from tse_analytics.core.manager import Manager
from tse_datatools.analysis.outliers_params import OutliersParams


class OutliersWidget(QScrollArea):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.setWidgetResizable(True)

        widget = QWidget(self)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        widget.setLayout(layout)

        layout.addWidget(QLabel("Coefficient:"))
        self.coefficient_spinbox = QDoubleSpinBox()
        self.coefficient_spinbox.setValue(1.5)
        self.coefficient_spinbox.valueChanged.connect(self._coefficient_changed)
        layout.addWidget(self.coefficient_spinbox)

        self.apply_outliers_checkbox = QCheckBox("Detect Outliers")
        self.apply_outliers_checkbox.stateChanged.connect(self._apply_outliers_changed)
        layout.addWidget(self.apply_outliers_checkbox)

        self.setWidget(widget)

    @QtCore.Slot(int)
    def _coefficient_changed(self, value: int):
        self.__outliers_params_changed()

    @QtCore.Slot(int)
    def _apply_outliers_changed(self, value: int):
        self.__outliers_params_changed()
        # Manager.data.detect_outliers = (value == 2)
        # if Manager.data.selected_dataset is not None:
        #     if Manager.data.apply_binning:
        #         Manager.messenger.broadcast(BinningAppliedMessage(self, Manager.data.binning_params))
        #     else:
        #         Manager.messenger.broadcast(RevertBinningMessage(self))

    def __outliers_params_changed(self):
        apply = self.apply_outliers_checkbox.isChecked()
        outliers_coefficient = self.coefficient_spinbox.value()

        outliers_params = OutliersParams(apply, outliers_coefficient)
        Manager.data.outliers_params = outliers_params

    def minimumSizeHint(self):
        return QSize(200, 40)
