from PySide6.QtCore import QTime
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
        time = QTime(
            meal_details_settings.intermeal_interval.hour,
            meal_details_settings.intermeal_interval.minute,
            meal_details_settings.intermeal_interval.second,
        )
        self.ui.intermealIntervalTimeEdit.setTime(time)
        self.ui.drinkingMinimumAmountDoubleSpinBox.setValue(meal_details_settings.drinking_minimum_amount)
        self.ui.feedingMinimumAmountDoubleSpinBox.setValue(meal_details_settings.feeding_minimum_amount)

    def set_data(self, dataset: Dataset):
        self.dataset = dataset

    def get_meal_details_settings(self) -> MealDetailsSettings:
        intermeal_interval = self.ui.intermealIntervalTimeEdit.time().toPython()
        drinking_minimum_amount = self.ui.drinkingMinimumAmountDoubleSpinBox.value()
        feeding_minimum_amount = self.ui.feedingMinimumAmountDoubleSpinBox.value()

        return MealDetailsSettings(intermeal_interval, drinking_minimum_amount, feeding_minimum_amount)
