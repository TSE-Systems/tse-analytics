from PySide6.QtCore import QTime
from PySide6.QtWidgets import QWidget

from tse_analytics.modules.phenomaster.data.dataset import Dataset
from tse_analytics.modules.phenomaster.meal_details.meal_details_settings import MealDetailsSettings
from tse_analytics.modules.phenomaster.meal_details.views.meal_details_settings_widget_ui import (
    Ui_MealDetailsSettingsWidget,
)


class MealDetailsSettingsWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_MealDetailsSettingsWidget()
        self.ui.setupUi(self)

        self.ui.pushButtonResetSettings.clicked.connect(self.__reset_settings)
        self.ui.radioButtonSequentialType.toggled.connect(lambda state: self.__set_analysis_type(state))

        self.dataset: Dataset | None = None

    def __set_analysis_type(self, sequential_meal_analysis: bool):
        self.ui.groupBoxSequentialSettings.setVisible(sequential_meal_analysis)
        self.ui.groupBoxIntervalSettings.setVisible(not sequential_meal_analysis)

    def __reset_settings(self):
        meal_details_settings = MealDetailsSettings.get_default()
        self.set_settings(meal_details_settings)

    def set_settings(self, meal_details_settings: MealDetailsSettings):
        self.__set_analysis_type(meal_details_settings.sequential_analysis_type)
        self.ui.radioButtonSequentialType.setChecked(meal_details_settings.sequential_analysis_type)
        self.ui.radioButtonIntervalType.setChecked(not meal_details_settings.sequential_analysis_type)
        self.ui.intermealIntervalTimeEdit.setTime(
            QTime(
                meal_details_settings.intermeal_interval.hour,
                meal_details_settings.intermeal_interval.minute,
                meal_details_settings.intermeal_interval.second,
            )
        )
        self.ui.drinkingMinimumAmountDoubleSpinBox.setValue(meal_details_settings.drinking_minimum_amount)
        self.ui.feedingMinimumAmountDoubleSpinBox.setValue(meal_details_settings.feeding_minimum_amount)
        self.ui.fixedIntervalTimeEdit.setTime(
            QTime(
                meal_details_settings.fixed_interval.hour,
                meal_details_settings.fixed_interval.minute,
                meal_details_settings.fixed_interval.second,
            )
        )

    def set_data(self, dataset: Dataset):
        self.dataset = dataset

    def get_meal_details_settings(self) -> MealDetailsSettings:
        sequential_analysis_type = self.ui.radioButtonSequentialType.isChecked()
        intermeal_interval = self.ui.intermealIntervalTimeEdit.time().toPython()
        drinking_minimum_amount = self.ui.drinkingMinimumAmountDoubleSpinBox.value()
        feeding_minimum_amount = self.ui.feedingMinimumAmountDoubleSpinBox.value()
        fixed_interval = self.ui.fixedIntervalTimeEdit.time().toPython()

        return MealDetailsSettings(
            sequential_analysis_type,
            intermeal_interval,
            drinking_minimum_amount,
            feeding_minimum_amount,
            fixed_interval,
        )
