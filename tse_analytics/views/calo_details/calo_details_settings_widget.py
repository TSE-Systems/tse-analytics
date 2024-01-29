from PySide6.QtWidgets import QWidget

from tse_analytics.calo_details.calo_details_settings import CaloDetailsSettings
from tse_analytics.data.dataset import Dataset

from tse_analytics.views.calo_details.calo_details_settings_widget_ui import Ui_CaloDetailsSettingsWidget


class CaloDetailsSettingsWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_CaloDetailsSettingsWidget()
        self.ui.setupUi(self)

        self.dataset: Dataset | None = None

    def set_settings(self, calo_details_settings: CaloDetailsSettings):
        self.ui.iterationsSpinBox.setValue(calo_details_settings.iterations)
        self.ui.predictionOffsetSpinBox.setValue(calo_details_settings.prediction_offset)

        self.ui.widgetO2Settings.set_data(
            calo_details_settings.o2_settings,
        )

        self.ui.widgetCO2Settings.set_data(
            calo_details_settings.co2_settings,
        )

    def set_data(self, dataset: Dataset):
        self.dataset = dataset
        flow_value = 0.5
        if "Flow" in dataset.original_df.columns:
            flow_value = dataset.original_df.iloc[1].at["Flow"]
        self.ui.flowDoubleSpinBox.setValue(flow_value)

    def get_calo_details_settings(self) -> CaloDetailsSettings:
        iterations = self.ui.iterationsSpinBox.value()
        prediction_offset = self.ui.predictionOffsetSpinBox.value()
        flow = self.ui.flowDoubleSpinBox.value()

        o2_gas_settings = self.ui.widgetO2Settings.get_gas_settings()
        co2_gas_settings = self.ui.widgetCO2Settings.get_gas_settings()

        return CaloDetailsSettings(iterations, prediction_offset, flow, o2_gas_settings, co2_gas_settings)
