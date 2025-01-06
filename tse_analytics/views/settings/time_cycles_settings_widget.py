from PySide6.QtCore import QTime
from PySide6.QtWidgets import QWidget

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.views.settings.time_cycles_settings_widget_ui import Ui_TimeCyclesSettingsWidget


class TimeCyclesSettingsWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_TimeCyclesSettingsWidget()
        self.ui.setupUi(self)

        self.dataset: Dataset | None = None

        self.ui.timeEditLightCycleStart.editingFinished.connect(self._light_cycle_start_changed)
        self.ui.timeEditDarkCycleStart.editingFinished.connect(self._dark_cycle_start_changed)

    def set_data(self, dataset: Dataset):
        self.dataset = dataset
        self.ui.timeEditLightCycleStart.setTime(
            QTime(self.dataset.binning_settings.time_cycles_settings.light_cycle_start)
        )
        self.ui.timeEditDarkCycleStart.setTime(
            QTime(self.dataset.binning_settings.time_cycles_settings.dark_cycle_start)
        )

    def _light_cycle_start_changed(self):
        if self.dataset is None:
            return
        self.dataset.binning_settings.time_cycles_settings.light_cycle_start = (
            self.ui.timeEditLightCycleStart.time().toPython()
        )

    def _dark_cycle_start_changed(self):
        if self.dataset is None:
            return
        self.dataset.binning_settings.time_cycles_settings.dark_cycle_start = (
            self.ui.timeEditDarkCycleStart.time().toPython()
        )
