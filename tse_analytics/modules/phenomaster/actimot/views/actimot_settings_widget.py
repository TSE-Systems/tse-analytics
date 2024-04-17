from PySide6.QtCore import QTime
from PySide6.QtWidgets import QWidget

from tse_analytics.modules.phenomaster.actimot.actimot_settings import ActimotSettings
from tse_analytics.modules.phenomaster.actimot.views.actimot_settings_widget_ui import Ui_ActimotSettingsWidget
from tse_analytics.modules.phenomaster.data.dataset import Dataset


class ActimotSettingsWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_ActimotSettingsWidget()
        self.ui.setupUi(self)

        self.ui.pushButtonResetSettings.clicked.connect(self.__reset_settings)
        self.ui.radioButtonSequentialType.toggled.connect(lambda state: self.__set_analysis_type(state))

        self.dataset: Dataset | None = None

    def set_data(self, dataset: Dataset, actimot_settings: ActimotSettings):
        self.dataset = dataset
        self.__set_settings(actimot_settings)

    def __set_settings(self, actimot_settings: ActimotSettings):
        # self.__set_analysis_type(meal_details_settings.sequential_analysis_type)
        # self.ui.radioButtonSequentialType.setChecked(meal_details_settings.sequential_analysis_type)
        # self.ui.radioButtonIntervalType.setChecked(not meal_details_settings.sequential_analysis_type)
        # self.ui.intermealIntervalTimeEdit.setTime(
        #     QTime(
        #         meal_details_settings.intermeal_interval.hour,
        #         meal_details_settings.intermeal_interval.minute,
        #         meal_details_settings.intermeal_interval.second,
        #     )
        # )
        # self.ui.drinkingMinimumAmountDoubleSpinBox.setValue(meal_details_settings.drinking_minimum_amount)
        # self.ui.feedingMinimumAmountDoubleSpinBox.setValue(meal_details_settings.feeding_minimum_amount)
        # self.ui.fixedIntervalTimeEdit.setTime(
        #     QTime(
        #         meal_details_settings.fixed_interval.hour,
        #         meal_details_settings.fixed_interval.minute,
        #         meal_details_settings.fixed_interval.second,
        #     )
        # )
        pass

    def __set_analysis_type(self, sequential_meal_analysis: bool):
        self.ui.groupBoxSequentialSettings.setVisible(sequential_meal_analysis)
        self.ui.groupBoxIntervalSettings.setVisible(not sequential_meal_analysis)

    def __reset_settings(self):
        settings = ActimotSettings.get_default()
        self.__set_settings(settings)

    def get_settings(self) -> ActimotSettings:
        return ActimotSettings()
