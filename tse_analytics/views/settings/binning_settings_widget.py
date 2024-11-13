from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget

from tse_analytics.core import messaging
from tse_analytics.core.data.binning import BinningMode
from tse_analytics.modules.phenomaster.data.dataset import Dataset
from tse_analytics.views.settings.binning_settings_widget_ui import Ui_BinningSettingsWidget


class BinningSettingsWidget(QWidget, messaging.MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_BinningSettingsWidget()
        self.ui.setupUi(self)

        messaging.subscribe(self, messaging.DatasetChangedMessage, self._on_dataset_changed)

        self.ui.widgetTimeCyclesSettings.setVisible(False)
        self.ui.widgetTimePhasesSettings.setVisible(False)

        self.ui.applyBinningCheckBox.stateChanged.connect(self._apply_binning_changed)

        self.ui.binningModeComboBox.addItems(list(BinningMode))
        self.ui.binningModeComboBox.currentTextChanged.connect(self._binning_mode_changed)

        self.dataset: Dataset | None = None

    def _on_dataset_changed(self, message: messaging.DatasetChangedMessage):
        self.dataset = message.dataset
        if self.dataset is None:
            self.ui.applyBinningCheckBox.setChecked(False)
            self.ui.binningModeComboBox.setCurrentText(BinningMode.INTERVALS)
            self.ui.widgetTimePhasesSettings.clear()
        else:
            self.ui.widgetTimeIntervalSettings.set_data(self.dataset)
            self.ui.widgetTimeCyclesSettings.set_data(self.dataset)
            self.ui.widgetTimePhasesSettings.set_data(self.dataset)
            self.ui.binningModeComboBox.setCurrentText(self.dataset.binning_settings.mode)
            self.ui.applyBinningCheckBox.setChecked(self.dataset.binning_settings.apply)

    def _binning_mode_changed(self, value: str):
        match value:
            case BinningMode.INTERVALS:
                self.ui.widgetTimeIntervalSettings.setVisible(True)
                self.ui.widgetTimeCyclesSettings.setVisible(False)
                self.ui.widgetTimePhasesSettings.setVisible(False)
            case BinningMode.CYCLES:
                self.ui.widgetTimeIntervalSettings.setVisible(False)
                self.ui.widgetTimeCyclesSettings.setVisible(True)
                self.ui.widgetTimePhasesSettings.setVisible(False)
            case BinningMode.PHASES:
                self.ui.widgetTimeIntervalSettings.setVisible(False)
                self.ui.widgetTimeCyclesSettings.setVisible(False)
                self.ui.widgetTimePhasesSettings.setVisible(True)

        if self.dataset is not None:
            binning_settings = self.dataset.binning_settings
            binning_settings.mode = BinningMode(self.ui.binningModeComboBox.currentText())
            self.dataset.apply_binning(binning_settings)

    def _apply_binning_changed(self, value: int):
        if self.dataset is not None:
            binning_settings = self.dataset.binning_settings
            binning_settings.apply = self.ui.applyBinningCheckBox.isChecked()
            self.dataset.apply_binning(binning_settings)

    def minimumSizeHint(self):
        return QSize(300, 70)
