from PySide6.QtWidgets import QWidget
from tse_analytics.data.time_intervals_binning_settings import TimeIntervalsBinningSettings

from tse_analytics.core.manager import Manager
from tse_analytics.views.settings.time_intervals_settings_widget_ui import Ui_TimeIntervalsSettingsWidget


class TimeIntervalsSettingsWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_TimeIntervalsSettingsWidget()
        self.ui.setupUi(self)

        self.ui.unitComboBox.addItems(["day", "hour", "minute"])
        self.ui.unitComboBox.currentTextChanged.connect(self.__binning_unit_changed)

        self.ui.deltaSpinBox.valueChanged.connect(self.__binning_delta_changed)

    def set_data(self, time_intervals_settings: TimeIntervalsBinningSettings):
        self.ui.unitComboBox.setCurrentText(time_intervals_settings.unit)
        self.ui.deltaSpinBox.setValue(time_intervals_settings.delta)

    def __binning_unit_changed(self, value: str):
        if Manager.data.selected_dataset is None:
            return
        Manager.data.selected_dataset.binning_settings.time_intervals_settings.unit = value

    def __binning_delta_changed(self, value: int):
        if Manager.data.selected_dataset is None:
            return
        Manager.data.selected_dataset.binning_settings.time_intervals_settings.delta = value
