from PySide6.QtCore import QTime
from PySide6.QtWidgets import QWidget
from tse_datatools.data.time_cycles_binning_settings import TimeCyclesBinningSettings

from tse_analytics.core.manager import Manager
from tse_analytics.views.settings.time_cycles_settings_widget_ui import Ui_TimeCyclesSettingsWidget


class TimeCyclesSettingsWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_TimeCyclesSettingsWidget()
        self.ui.setupUi(self)

        self.ui.timeEditLightCycleStart.editingFinished.connect(self.__light_cycle_start_changed)
        self.ui.timeEditDarkCycleStart.editingFinished.connect(self.__dark_cycle_start_changed)

    def set_data(self, time_cycles_settings: TimeCyclesBinningSettings):
        self.ui.timeEditLightCycleStart.setTime(QTime(time_cycles_settings.light_cycle_start))
        self.ui.timeEditDarkCycleStart.setTime(QTime(time_cycles_settings.dark_cycle_start))

    def __light_cycle_start_changed(self):
        if Manager.data.selected_dataset is None:
            return
        Manager.data.selected_dataset.binning_settings.time_cycles_settings.light_cycle_start = (
            self.ui.timeEditLightCycleStart.time().toPython()
        )

    def __dark_cycle_start_changed(self):
        if Manager.data.selected_dataset is None:
            return
        Manager.data.selected_dataset.binning_settings.time_cycles_settings.dark_cycle_start = (
            self.ui.timeEditDarkCycleStart.time().toPython()
        )
