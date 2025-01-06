from PySide6.QtWidgets import QWidget

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.views.settings.time_intervals_settings_widget_ui import Ui_TimeIntervalsSettingsWidget


class TimeIntervalsSettingsWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_TimeIntervalsSettingsWidget()
        self.ui.setupUi(self)

        self.dataset: Dataset | None = None

        self.ui.unitComboBox.addItems(["day", "hour", "minute"])
        self.ui.unitComboBox.currentTextChanged.connect(self._binning_unit_changed)

        self.ui.deltaSpinBox.valueChanged.connect(self._binning_delta_changed)

    def set_data(self, dataset: Dataset):
        self.dataset = dataset
        self.ui.unitComboBox.setCurrentText(self.dataset.binning_settings.time_intervals_settings.unit)
        self.ui.deltaSpinBox.setValue(self.dataset.binning_settings.time_intervals_settings.delta)

    def _binning_unit_changed(self, value: str):
        if self.dataset is None:
            return
        self.dataset.binning_settings.time_intervals_settings.unit = value

    def _binning_delta_changed(self, value: int):
        if self.dataset is None:
            return
        self.dataset.binning_settings.time_intervals_settings.delta = value
