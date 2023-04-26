from typing import Optional

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget

from tse_analytics.core.manager import Manager
from tse_analytics.views.settings.outliers_settings_widget_ui import Ui_OutliersSettingsWidget
from tse_datatools.analysis.outliers_params import OutliersParams


class OutliersSettingsWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.ui = Ui_OutliersSettingsWidget()
        self.ui.setupUi(self)

        self.ui.checkBoxDetect.stateChanged.connect(self.__detect_outliers_changed)

        self.ui.doubleSpinBoxCoefficient.setValue(Manager.data.outliers_params.coefficient)
        self.ui.doubleSpinBoxCoefficient.valueChanged.connect(self.__coefficient_changed)

    def __detect_outliers_changed(self, value: int):
        self.__outliers_params_changed()
        # Manager.data.detect_outliers = (value == 2)
        # if Manager.data.selected_dataset is not None:
        #     if Manager.data.apply_binning:
        #         Manager.messenger.broadcast(BinningAppliedMessage(self, Manager.data.binning_params))
        #     else:
        #         Manager.messenger.broadcast(RevertBinningMessage(self))

    def __coefficient_changed(self, value: int):
        self.__outliers_params_changed()

    def __outliers_params_changed(self):
        apply = self.ui.checkBoxDetect.isChecked()
        outliers_coefficient = self.ui.doubleSpinBoxCoefficient.value()

        outliers_params = OutliersParams(apply, outliers_coefficient)
        Manager.data.outliers_params = outliers_params

    def minimumSizeHint(self):
        return QSize(200, 40)
