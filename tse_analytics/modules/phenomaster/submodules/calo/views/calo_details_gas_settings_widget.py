from PySide6.QtWidgets import QWidget

from tse_analytics.modules.phenomaster.submodules.calo.calo_data_settings import CaloDataGasSettings
from tse_analytics.modules.phenomaster.submodules.calo.views.calo_details_gas_settings_widget_ui import (
    Ui_CaloDetailsGasSettingsWidget,
)


class CaloDetailsGasSettingsWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_CaloDetailsGasSettingsWidget()
        self.ui.setupUi(self)

        self.ui.doubleSpinBoxMinA.setRange(-float("inf"), float("inf"))
        self.ui.doubleSpinBoxMaxA.setRange(-float("inf"), float("inf"))

        self.ui.doubleSpinBoxMinB.setRange(-float("inf"), float("inf"))
        self.ui.doubleSpinBoxMaxB.setRange(-float("inf"), float("inf"))

        self.ui.doubleSpinBoxMinC.setRange(-float("inf"), float("inf"))
        self.ui.doubleSpinBoxMaxC.setRange(-float("inf"), float("inf"))

        self.ui.doubleSpinBoxRefMinA.setRange(-float("inf"), float("inf"))
        self.ui.doubleSpinBoxRefMaxA.setRange(-float("inf"), float("inf"))

        self.ui.doubleSpinBoxRefMinB.setRange(-float("inf"), float("inf"))
        self.ui.doubleSpinBoxRefMaxB.setRange(-float("inf"), float("inf"))

        self.ui.doubleSpinBoxRefMinC.setRange(-float("inf"), float("inf"))
        self.ui.doubleSpinBoxRefMaxC.setRange(-float("inf"), float("inf"))

    def set_data(
        self,
        calo_details_gas_settings: CaloDataGasSettings,
    ):
        self.ui.titleGroupBox.setTitle(calo_details_gas_settings.gas_name)

        self.ui.spinBoxStartOffset.setValue(calo_details_gas_settings.start_offset)
        self.ui.spinBoxEndOffset.setValue(calo_details_gas_settings.end_offset)

        self.ui.doubleSpinBoxMinA.setValue(calo_details_gas_settings.bounds[0][0])
        self.ui.doubleSpinBoxMaxA.setValue(calo_details_gas_settings.bounds[1][0])

        self.ui.doubleSpinBoxMinB.setValue(calo_details_gas_settings.bounds[0][1])
        self.ui.doubleSpinBoxMaxB.setValue(calo_details_gas_settings.bounds[1][1])

        self.ui.doubleSpinBoxMinC.setValue(calo_details_gas_settings.bounds[0][2])
        self.ui.doubleSpinBoxMaxC.setValue(calo_details_gas_settings.bounds[1][2])

        self.ui.doubleSpinBoxRefMinA.setValue(calo_details_gas_settings.ref_bounds[0][0])
        self.ui.doubleSpinBoxRefMaxA.setValue(calo_details_gas_settings.ref_bounds[1][0])

        self.ui.doubleSpinBoxRefMinB.setValue(calo_details_gas_settings.ref_bounds[0][1])
        self.ui.doubleSpinBoxRefMaxB.setValue(calo_details_gas_settings.ref_bounds[1][1])

        self.ui.doubleSpinBoxRefMinC.setValue(calo_details_gas_settings.ref_bounds[0][2])
        self.ui.doubleSpinBoxRefMaxC.setValue(calo_details_gas_settings.ref_bounds[1][2])

    def get_gas_settings(self) -> CaloDataGasSettings:
        bounds = (
            (self.ui.doubleSpinBoxMinA.value(), self.ui.doubleSpinBoxMinB.value(), self.ui.doubleSpinBoxMinC.value()),
            (self.ui.doubleSpinBoxMaxA.value(), self.ui.doubleSpinBoxMaxB.value(), self.ui.doubleSpinBoxMaxC.value()),
        )
        ref_bounds = (
            (
                self.ui.doubleSpinBoxRefMinA.value(),
                self.ui.doubleSpinBoxRefMinB.value(),
                self.ui.doubleSpinBoxRefMinC.value(),
            ),
            (
                self.ui.doubleSpinBoxRefMaxA.value(),
                self.ui.doubleSpinBoxRefMaxB.value(),
                self.ui.doubleSpinBoxRefMaxC.value(),
            ),
        )
        return CaloDataGasSettings(
            self.ui.titleGroupBox.title(),
            self.ui.spinBoxStartOffset.value(),
            self.ui.spinBoxEndOffset.value(),
            bounds,
            ref_bounds,
        )
