from typing import Optional

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget

from tse_analytics.core.manager import Manager
from tse_analytics.views.settings.time_settings_widget_ui import Ui_TimeSettingsWidget
from tse_datatools.analysis.time_cycles_params import TimeCyclesParams


class TimeSettingsWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.ui = Ui_TimeSettingsWidget()
        self.ui.setupUi(self)

        self.ui.checkBoxApply.stateChanged.connect(self.__apply_time_cycles_changed)
        self.ui.timeEditLightCycleStart.editingFinished.connect(self.__light_cycle_start_changed)
        self.ui.timeEditDarkCycleStart.editingFinished.connect(self.__dark_cycle_start_changed)

    def __apply_time_cycles_changed(self, value: int):
        self.__time_cycles_params_changed()

    def __light_cycle_start_changed(self):
        self.__time_cycles_params_changed()

    def __dark_cycle_start_changed(self):
        self.__time_cycles_params_changed()

    def __time_cycles_params_changed(self):
        apply = self.ui.checkBoxApply.isChecked()
        light_cycle_start = self.ui.timeEditLightCycleStart.time().toPython()
        dark_cycle_start = self.ui.timeEditDarkCycleStart.time().toPython()
        params = TimeCyclesParams(apply, light_cycle_start, dark_cycle_start)
        Manager.data.time_cycles_params = params

    def minimumSizeHint(self):
        return QSize(200, 40)
