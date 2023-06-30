from typing import Optional

from PySide6.QtWidgets import QWidget

from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import (
    ClearDataMessage,
    DatasetChangedMessage,
    BinningAppliedMessage,
    RevertBinningMessage,
    DataChangedMessage,
    GroupingModeChangedMessage,
)
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.views.data.data_plot_widget_ui import Ui_DataPlotWidget


class DataPlotWidget(QWidget, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_DataPlotWidget()
        self.ui.setupUi(self)

        self.ui.variableSelector.currentTextChanged.connect(self.__variable_changed)
        self.ui.toolButtonDisplayErrors.toggled.connect(self.__display_errors)

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)
        messenger.subscribe(self, ClearDataMessage, self.__on_clear_data)
        messenger.subscribe(self, BinningAppliedMessage, self.__on_binning_applied)
        messenger.subscribe(self, RevertBinningMessage, self.__on_revert_binning)
        messenger.subscribe(self, DataChangedMessage, self.__on_data_changed)
        messenger.subscribe(self, GroupingModeChangedMessage, self.__on_grouping_mode_changed)

    def __variable_changed(self, variable: str):
        Manager.data.selected_variable = variable
        self.ui.plotView.set_variable(variable)

    def __display_errors(self, state: bool):
        self.ui.plotView.set_display_errors(state)

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        self.ui.variableSelector.set_data(message.data.variables)
        self.__assign_data()

    def __assign_data(self):
        df = Manager.data.get_current_df(calculate_error=True)
        self.ui.plotView.set_data(df)

    def __on_clear_data(self, message: ClearDataMessage):
        self.ui.variableSelector.clear()
        self.ui.plotView.clear_plot()

    def __on_binning_applied(self, message: BinningAppliedMessage):
        self.__assign_data()

    def __on_revert_binning(self, message: RevertBinningMessage):
        self.__assign_data()

    def __on_data_changed(self, message: DataChangedMessage):
        self.__assign_data()

    def __on_grouping_mode_changed(self, message: GroupingModeChangedMessage):
        self.__assign_data()
