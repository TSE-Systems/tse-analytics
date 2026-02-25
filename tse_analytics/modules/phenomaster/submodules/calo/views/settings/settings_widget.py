from PySide6.QtWidgets import QWidget

from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset
from tse_analytics.modules.phenomaster.submodules.calo.calo_settings import CaloSettings
from tse_analytics.modules.phenomaster.submodules.calo.views.settings.settings_widget_ui import Ui_SettingsWidget


class SettingsWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_SettingsWidget()
        self.ui.setupUi(self)

        self.dataset: PhenoMasterDataset | None = None

    def set_settings(self, settings: CaloSettings):
        self.ui.iterationsSpinBox.setValue(settings.iterations)
        self.ui.predictionOffsetSpinBox.setValue(settings.prediction_offset)

        self.ui.widgetO2Settings.set_data(
            settings.o2_settings,
        )

        self.ui.widgetCO2Settings.set_data(
            settings.co2_settings,
        )

    def set_data(self, dataset: PhenoMasterDataset):
        self.dataset = dataset
        flow_value = 0.5
        main_datatable = dataset.datatables["Main"]
        if "Flow" in main_datatable.df.columns:
            flow_value = main_datatable.df.iloc[1].at["Flow"]
        self.ui.flowDoubleSpinBox.setValue(flow_value)

    def get_calo_settings(self) -> CaloSettings:
        iterations = self.ui.iterationsSpinBox.value()
        prediction_offset = self.ui.predictionOffsetSpinBox.value()
        flow = self.ui.flowDoubleSpinBox.value()

        o2_gas_settings = self.ui.widgetO2Settings.get_gas_settings()
        co2_gas_settings = self.ui.widgetCO2Settings.get_gas_settings()

        return CaloSettings(iterations, prediction_offset, flow, o2_gas_settings, co2_gas_settings)
