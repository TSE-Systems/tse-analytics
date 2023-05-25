from typing import Optional

from PySide6.QtWidgets import QWidget

from tse_analytics.views.calo_details.calo_details_settings import CaloDetailsSettings
from tse_analytics.views.calo_details.calo_details_settings_widget_ui import Ui_CaloDetailsSettingsWidget
from tse_datatools.data.dataset import Dataset


class CaloDetailsSettingsWidget(QWidget):
    def __init__(self, calo_details_settings: CaloDetailsSettings, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.ui = Ui_CaloDetailsSettingsWidget()
        self.ui.setupUi(self)

        self.ui.iterationsSpinBox.setValue(calo_details_settings.iterations)
        self.ui.predictionOffsetSpinBox.setValue(calo_details_settings.iterations)

        self.ui.widgetO2Settings.set_data(
            "O2",
            calo_details_settings.o2_settings,
            ((-3.75e+12, -9.0, 0), (2.389e+12, 0, 25)),
            ((-3.75e+12, -9.0, 0), (2.389e+12, 0, 25))
        )

        self.ui.widgetCO2Settings.set_data(
            "CO2",
            calo_details_settings.co2_settings,
            ((-3.75e+12, -9.0, 0), (2.389e+12, 0, 1)),
            ((-1.381e+12, -8.806, 0), (2.525e+12, 0, 0.1))
        )

        self.dataset: Optional[Dataset] = None

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

        return CaloDetailsSettings(
            iterations,
            prediction_offset,
            flow,
            o2_gas_settings,
            co2_gas_settings
        )
