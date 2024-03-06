from PySide6.QtWidgets import QWidget

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.modules.phenomaster.meal_details.meal_details_settings import MealDetailsSettings
from tse_analytics.views.meal_details.meal_details_settings_widget_ui import Ui_MealDetailsSettingsWidget


class MealDetailsSettingsWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_MealDetailsSettingsWidget()
        self.ui.setupUi(self)

        self.dataset: Dataset | None = None

    def set_settings(self, meal_details_settings: MealDetailsSettings):
        self.ui.iterationsSpinBox.setValue(meal_details_settings.iterations)
        self.ui.predictionOffsetSpinBox.setValue(meal_details_settings.prediction_offset)

    def set_data(self, dataset: Dataset):
        self.dataset = dataset
        flow_value = 0.5
        if "Flow" in dataset.original_df.columns:
            flow_value = dataset.original_df.iloc[1].at["Flow"]
        self.ui.flowDoubleSpinBox.setValue(flow_value)

    def get_meal_details_settings(self) -> MealDetailsSettings:
        iterations = self.ui.iterationsSpinBox.value()
        prediction_offset = self.ui.predictionOffsetSpinBox.value()
        flow = self.ui.flowDoubleSpinBox.value()

        return MealDetailsSettings(iterations, prediction_offset, flow)
