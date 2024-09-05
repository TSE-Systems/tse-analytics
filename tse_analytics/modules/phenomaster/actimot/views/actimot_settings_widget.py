from PySide6.QtWidgets import QWidget

from tse_analytics.modules.phenomaster.actimot.actimot_settings import ActimotSettings
from tse_analytics.modules.phenomaster.actimot.views.actimot_settings_widget_ui import Ui_ActimotSettingsWidget
from tse_analytics.modules.phenomaster.data.dataset import Dataset


class ActimotSettingsWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_ActimotSettingsWidget()
        self.ui.setupUi(self)

        self.ui.pushButtonResetSettings.clicked.connect(self._reset_settings)
        self.ui.radioButtonSequentialType.toggled.connect(lambda toggled: self._set_analysis_type(toggled))

        self.dataset: Dataset | None = None

    def set_data(self, dataset: Dataset, actimot_settings: ActimotSettings):
        self.dataset = dataset
        self._set_settings(actimot_settings)

    def _set_settings(self, actimot_settings: ActimotSettings):
        pass

    def _set_analysis_type(self, sequential_meal_analysis: bool):
        self.ui.groupBoxSequentialSettings.setVisible(sequential_meal_analysis)
        self.ui.groupBoxIntervalSettings.setVisible(not sequential_meal_analysis)

    def _reset_settings(self):
        settings = ActimotSettings.get_default()
        self._set_settings(settings)

    def get_settings(self) -> ActimotSettings:
        return ActimotSettings()
