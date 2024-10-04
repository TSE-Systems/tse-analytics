from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget

from tse_analytics.core.data.binning import BinningMode
from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import DatasetChangedMessage
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.messaging.messenger_listener import MessengerListener
from tse_analytics.modules.phenomaster.data.dataset import Dataset
from tse_analytics.views.settings.binning_settings_widget_ui import Ui_BinningSettingsWidget


class BinningSettingsWidget(QWidget, MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_BinningSettingsWidget()
        self.ui.setupUi(self)

        self.ui.widgetTimeCyclesSettings.setVisible(False)
        self.ui.widgetTimePhasesSettings.setVisible(False)

        self.ui.applyBinningCheckBox.stateChanged.connect(self._apply_binning_changed)

        self.ui.binningModeComboBox.addItems((e for e in BinningMode))
        self.ui.binningModeComboBox.currentTextChanged.connect(self._binning_mode_changed)

        self.dataset: Dataset | None = None

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self._on_dataset_changed)

    def _on_dataset_changed(self, message: DatasetChangedMessage):
        if message.data is None:
            self.dataset = None
            self.ui.applyBinningCheckBox.setChecked(False)
            self.ui.binningModeComboBox.setCurrentText(BinningMode.INTERVALS)
            self.ui.widgetTimePhasesSettings.clear()
        else:
            self.dataset = message.data
            self.ui.widgetTimeIntervalSettings.set_data(self.dataset.binning_settings.time_intervals_settings)
            self.ui.widgetTimeCyclesSettings.set_data(self.dataset.binning_settings.time_cycles_settings)
            self.ui.widgetTimePhasesSettings.set_data(self.dataset.binning_settings.time_phases_settings)
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
            Manager.data.apply_binning(binning_settings)

    def _apply_binning_changed(self, value: int):
        if self.dataset is not None:
            binning_settings = self.dataset.binning_settings
            binning_settings.apply = self.ui.applyBinningCheckBox.isChecked()
            Manager.data.apply_binning(binning_settings)

    def minimumSizeHint(self):
        return QSize(300, 70)
