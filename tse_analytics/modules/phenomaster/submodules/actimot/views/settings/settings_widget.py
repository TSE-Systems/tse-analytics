from PySide6.QtWidgets import QWidget

from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset
from tse_analytics.modules.phenomaster.submodules.actimot.actimot_settings import ActimotSettings
from tse_analytics.modules.phenomaster.submodules.actimot.views.settings.settings_widget_ui import Ui_SettingsWidget


class SettingsWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_SettingsWidget()
        self.ui.setupUi(self)

        self.ui.pushButtonResetSettings.clicked.connect(self._reset_settings)

        self.dataset: PhenoMasterDataset | None = None

    def set_data(self, dataset: PhenoMasterDataset, actimot_settings: ActimotSettings):
        self.dataset = dataset
        self._set_settings(actimot_settings)

    def _set_settings(self, settings: ActimotSettings):
        self.ui.groupBoxSmoothing.setChecked(settings.use_smooting)
        if settings.smoothing_window_size is None:
            self.ui.groupBoxWindowSize.setChecked(False)
        else:
            self.ui.groupBoxWindowSize.setChecked(True)
            self.ui.spinBoxWindowSize.setValue(settings.smoothing_window_size)
        self.ui.spinBoxPolynomialOrder.setValue(settings.smoothing_polynomial_order)

    def _reset_settings(self):
        settings = ActimotSettings.get_default()
        self._set_settings(settings)

    def get_settings(self) -> ActimotSettings:
        use_smoothing = self.ui.groupBoxSmoothing.isChecked()
        smoothing_window_size = self.ui.spinBoxWindowSize.value() if self.ui.groupBoxWindowSize.isChecked() else None
        smoothing_polynomial_order = self.ui.spinBoxPolynomialOrder.value()
        return ActimotSettings(
            use_smooting=use_smoothing,
            smoothing_window_size=smoothing_window_size,
            smoothing_polynomial_order=smoothing_polynomial_order,
        )
