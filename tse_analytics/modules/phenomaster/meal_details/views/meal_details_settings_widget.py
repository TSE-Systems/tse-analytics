from PySide6.QtCore import QTime
from PySide6.QtWidgets import QHeaderView, QInputDialog, QWidget

from tse_analytics.core.data.shared import AnimalDiet
from tse_analytics.modules.phenomaster.data.dataset import Dataset
from tse_analytics.modules.phenomaster.meal_details.meal_details_settings import MealDetailsSettings
from tse_analytics.modules.phenomaster.meal_details.models.diets_model import DietsModel
from tse_analytics.modules.phenomaster.meal_details.views.meal_details_settings_widget_ui import (
    Ui_MealDetailsSettingsWidget,
)


class MealDetailsSettingsWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_MealDetailsSettingsWidget()
        self.ui.setupUi(self)

        self.ui.pushButtonResetSettings.clicked.connect(self._reset_settings)
        self.ui.radioButtonSequentialType.toggled.connect(lambda toggled: self._set_analysis_type(toggled))

        self.ui.toolButtonAddDiet.clicked.connect(self._add_diet)
        self.ui.toolButtonDeleteDiet.clicked.connect(self._delete_diet)

        self.dataset: Dataset | None = None
        self.diets_model: DietsModel | None = None

    def set_data(self, dataset: Dataset, meal_details_settings: MealDetailsSettings):
        self.dataset = dataset
        self._set_settings(meal_details_settings)

        self.diets_model = DietsModel(meal_details_settings.diets)
        self.ui.tableViewDiets.setModel(self.diets_model)
        header = self.ui.tableViewDiets.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

    def _set_settings(self, meal_details_settings: MealDetailsSettings):
        self._set_analysis_type(meal_details_settings.sequential_analysis_type)
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

    def _set_analysis_type(self, sequential_meal_analysis: bool):
        self.ui.groupBoxSequentialSettings.setVisible(sequential_meal_analysis)
        self.ui.groupBoxIntervalSettings.setVisible(not sequential_meal_analysis)

    def _reset_settings(self):
        meal_details_settings = MealDetailsSettings.get_default()
        self._set_settings(meal_details_settings)

    def _add_diet(self):
        text, result = QInputDialog.getText(self, "Add Animal Diet", "Please enter diet name:")
        if result:
            diet = AnimalDiet(name=text, caloric_value=0.0)
            self.diets_model.add_diet(diet)

    def _delete_diet(self):
        indexes = self.ui.tableViewDiets.selectedIndexes()
        if indexes:
            # Indexes is a single-item list in single-select mode.
            index = indexes[0]
            self.diets_model.delete_diet(index)
            # Clear the selection (as it is no longer valid).
            self.ui.tableViewDiets.clearSelection()

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
            self.diets_model.items,
        )
