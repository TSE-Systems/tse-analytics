from typing import Optional

import pandas as pd
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget

from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import BinningAppliedMessage, RevertBinningMessage
from tse_analytics.views.settings.binning_settings_widget_ui import Ui_BinningSettingsWidget
from tse_datatools.analysis.binning_operation import BinningOperation
from tse_datatools.analysis.binning_params import BinningParams
from tse_datatools.analysis.grouping_mode import GroupingMode


class BinningSettingsWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.ui = Ui_BinningSettingsWidget()
        self.ui.setupUi(self)

        self.ui.groupingModeComboBox.addItems([e.value for e in GroupingMode])
        self.ui.groupingModeComboBox.currentTextChanged.connect(self.__grouping_mode_changed)

        self.ui.applyBinningCheckBox.stateChanged.connect(self.__apply_binning_changed)

        self.ui.unitComboBox.addItems(["day", "hour", "minute"])
        self.ui.unitComboBox.setCurrentText("hour")
        self.ui.unitComboBox.currentTextChanged.connect(self.__binning_unit_changed)

        self.ui.deltaSpinBox.setValue(1)
        self.ui.deltaSpinBox.valueChanged.connect(self.__binning_delta_changed)

        self.ui.operationComboBox.addItems([e.value for e in BinningOperation])
        self.ui.operationComboBox.setCurrentText("mean")
        self.ui.operationComboBox.currentTextChanged.connect(self.__binning_operation_changed)

    def __binning_unit_changed(self, value: str):
        self.__binning_params_changed()

    def __binning_delta_changed(self, value: int):
        self.__binning_params_changed()

    def __binning_operation_changed(self, value: str):
        self.__binning_params_changed()

    def __apply_binning_changed(self, value: int):
        Manager.data.binning_params.apply = value == 2
        if Manager.data.selected_dataset is not None:
            if Manager.data.binning_params.apply:
                Manager.messenger.broadcast(BinningAppliedMessage(self, Manager.data.binning_params))
            else:
                Manager.messenger.broadcast(RevertBinningMessage(self))

    def __grouping_mode_changed(self, text: str):
        Manager.data.set_grouping_mode(GroupingMode(text))

    def __binning_params_changed(self):
        unit = "H"
        unit_value = self.ui.unitComboBox.currentText()
        if unit_value == "day":
            unit = "D"
        elif unit_value == "hour":
            unit = "H"
        elif unit_value == "minute":
            unit = "min"

        binning_delta = self.ui.deltaSpinBox.value()

        timedelta = pd.Timedelta(f"{binning_delta}{unit}")

        binning_params = BinningParams(
            self.ui.applyBinningCheckBox.isChecked(),
            timedelta,
            BinningOperation(self.ui.operationComboBox.currentText()),
        )
        Manager.data.binning_params = binning_params

    def minimumSizeHint(self):
        return QSize(200, 40)
