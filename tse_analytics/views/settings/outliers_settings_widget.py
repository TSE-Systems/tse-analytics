from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget

from tse_analytics.core.data.outliers import OutliersMode, OutliersParams
from tse_analytics.core.manager import Manager
from tse_analytics.views.settings.outliers_settings_widget_ui import Ui_OutliersSettingsWidget


class OutliersSettingsWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_OutliersSettingsWidget()
        self.ui.setupUi(self)

        self.ui.outliersModeComboBox.addItems([e.value for e in OutliersMode])
        self.ui.outliersModeComboBox.currentTextChanged.connect(self.__outliers_mode_changed)

        self.ui.doubleSpinBoxCoefficient.setValue(Manager.data.outliers_params.coefficient)
        self.ui.doubleSpinBoxCoefficient.valueChanged.connect(self.__coefficient_changed)

    def __outliers_mode_changed(self, value: OutliersMode):
        match value:
            case OutliersMode.OFF.value:
                pass
            case OutliersMode.HIGHLIGHT.value:
                pass
            case OutliersMode.REMOVE.value:
                pass
        self.__outliers_params_changed()

    def __coefficient_changed(self, value: int):
        self.__outliers_params_changed()

    def __outliers_params_changed(self):
        mode = OutliersMode(self.ui.outliersModeComboBox.currentText())
        outliers_coefficient = self.ui.doubleSpinBoxCoefficient.value()

        outliers_params = OutliersParams(mode, outliers_coefficient)
        Manager.data.apply_outliers(outliers_params)

    def minimumSizeHint(self):
        return QSize(200, 40)
