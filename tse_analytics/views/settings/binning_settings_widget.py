
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget
from tse_datatools.analysis.binning_mode import BinningMode
from tse_datatools.analysis.binning_operation import BinningOperation
from tse_datatools.analysis.binning_params import BinningParams

from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import DatasetChangedMessage
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.views.settings.binning_settings_widget_ui import Ui_BinningSettingsWidget


class BinningSettingsWidget(QWidget, MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_BinningSettingsWidget()
        self.ui.setupUi(self)

        self.ui.widgetTimeCyclesSettings.setVisible(False)
        self.ui.widgetTimePhasesSettings.setVisible(False)

        self.ui.binningModeComboBox.addItems([e.value for e in BinningMode])
        self.ui.binningModeComboBox.currentTextChanged.connect(self.__binning_mode_changed)

        self.ui.applyBinningCheckBox.stateChanged.connect(self.__apply_binning_changed)

        self.ui.binningOperationComboBox.addItems([e.value for e in BinningOperation])
        self.ui.binningOperationComboBox.setCurrentText("mean")
        self.ui.binningOperationComboBox.currentTextChanged.connect(self.__binning_operation_changed)

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        if message.data is None:
            self.ui.widgetTimePhasesSettings.clear()
        else:
            self.ui.widgetTimeIntervalSettings.set_data(message.data.binning_settings.time_intervals_settings)
            self.ui.widgetTimeCyclesSettings.set_data(message.data.binning_settings.time_cycles_settings)
            self.ui.widgetTimePhasesSettings.set_data(message.data.binning_settings.time_phases_settings)

    def __binning_mode_changed(self, value: BinningMode):
        match value:
            case BinningMode.INTERVALS.value:
                self.ui.widgetTimeIntervalSettings.setVisible(True)
                self.ui.widgetTimeCyclesSettings.setVisible(False)
                self.ui.widgetTimePhasesSettings.setVisible(False)
            case BinningMode.CYCLES.value:
                self.ui.widgetTimeIntervalSettings.setVisible(False)
                self.ui.widgetTimeCyclesSettings.setVisible(True)
                self.ui.widgetTimePhasesSettings.setVisible(False)
            case BinningMode.PHASES.value:
                self.ui.widgetTimeIntervalSettings.setVisible(False)
                self.ui.widgetTimeCyclesSettings.setVisible(False)
                self.ui.widgetTimePhasesSettings.setVisible(True)
        self.__binning_params_changed()

    def __binning_operation_changed(self, value: str):
        self.__binning_params_changed()

    def __apply_binning_changed(self, value: int):
        self.__binning_params_changed()

    def __binning_params_changed(self):
        apply = self.ui.applyBinningCheckBox.isChecked()
        mode = BinningMode(self.ui.binningModeComboBox.currentText())
        operation = BinningOperation(self.ui.binningOperationComboBox.currentText())
        params = BinningParams(
            apply,
            mode,
            operation,
        )
        Manager.data.apply_binning(params)

    def minimumSizeHint(self):
        return QSize(200, 40)
