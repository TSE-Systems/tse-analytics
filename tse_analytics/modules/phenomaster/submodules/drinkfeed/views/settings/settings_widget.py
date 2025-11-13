from PySide6.QtCore import QTime
from PySide6.QtWidgets import QHeaderView, QInputDialog, QWidget

from tse_analytics.core.data.shared import AnimalDiet
from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset
from tse_analytics.modules.phenomaster.submodules.drinkfeed.drinkfeed_settings import DrinkFeedSettings
from tse_analytics.modules.phenomaster.submodules.drinkfeed.models.diets_model import DietsModel
from tse_analytics.modules.phenomaster.submodules.drinkfeed.views.settings.settings_widget_ui import Ui_SettingsWidget


class SettingsWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_SettingsWidget()
        self.ui.setupUi(self)

        self.ui.pushButtonResetSettings.clicked.connect(self._reset_settings)
        self.ui.radioButtonSequentialType.toggled.connect(lambda toggled: self._set_analysis_type(toggled))

        self.ui.toolButtonAddDiet.clicked.connect(self._add_diet)
        self.ui.toolButtonDeleteDiet.clicked.connect(self._delete_diet)

        self.dataset: PhenoMasterDataset | None = None
        self.diets_model: DietsModel | None = None

    def set_data(self, dataset: PhenoMasterDataset, drinkfeed_settings: DrinkFeedSettings):
        self.dataset = dataset
        self._set_settings(drinkfeed_settings)

        self.diets_model = DietsModel(drinkfeed_settings.diets)
        self.ui.tableViewDiets.setModel(self.diets_model)
        header = self.ui.tableViewDiets.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

    def _set_settings(self, settings: DrinkFeedSettings):
        self._set_analysis_type(settings.sequential_analysis_type)
        self.ui.radioButtonSequentialType.setChecked(settings.sequential_analysis_type)
        self.ui.radioButtonIntervalType.setChecked(not settings.sequential_analysis_type)
        self.ui.intermealIntervalTimeEdit.setTime(
            QTime(
                settings.intermeal_interval.hour,
                settings.intermeal_interval.minute,
                settings.intermeal_interval.second,
            )
        )
        self.ui.drinkingMinimumAmountDoubleSpinBox.setValue(settings.drinking_minimum_amount)
        self.ui.feedingMinimumAmountDoubleSpinBox.setValue(settings.feeding_minimum_amount)
        self.ui.fixedIntervalTimeEdit.setTime(
            QTime(
                settings.fixed_interval.hour,
                settings.fixed_interval.minute,
                settings.fixed_interval.second,
            )
        )

    def _set_analysis_type(self, sequential_analysis: bool):
        self.ui.groupBoxSequentialSettings.setVisible(sequential_analysis)
        self.ui.groupBoxIntervalSettings.setVisible(not sequential_analysis)

    def _reset_settings(self):
        settings = DrinkFeedSettings.get_default()
        self._set_settings(settings)

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

    def get_drinkfeed_settings(self) -> DrinkFeedSettings:
        sequential_analysis_type = self.ui.radioButtonSequentialType.isChecked()
        intermeal_interval = self.ui.intermealIntervalTimeEdit.time().toPython()
        drinking_minimum_amount = self.ui.drinkingMinimumAmountDoubleSpinBox.value()
        feeding_minimum_amount = self.ui.feedingMinimumAmountDoubleSpinBox.value()
        fixed_interval = self.ui.fixedIntervalTimeEdit.time().toPython()

        return DrinkFeedSettings(
            sequential_analysis_type,
            intermeal_interval,
            drinking_minimum_amount,
            feeding_minimum_amount,
            fixed_interval,
            self.diets_model.items,
        )
