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
from tse_analytics.views.data.bar_plot_view import BarPlotView
from tse_analytics.views.data.data_plot_widget_ui import Ui_DataPlotWidget
from tse_analytics.views.data.timeline_plot_view import TimelinePlotView
from tse_datatools.analysis.binning_mode import BinningMode


class DataPlotWidget(QWidget, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_DataPlotWidget()
        self.ui.setupUi(self)

        self.ui.variableSelector.currentTextChanged.connect(self.__variable_changed)
        self.ui.toolButtonDisplayErrors.toggled.connect(self.__display_errors)

        self.timelinePlotView = TimelinePlotView(self)
        self.barPlotView = BarPlotView(self)

        self.ui.verticalLayout.addWidget(self.timelinePlotView)
        self.active_binning_mode = BinningMode.INTERVALS

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)
        messenger.subscribe(self, ClearDataMessage, self.__on_clear_data)
        messenger.subscribe(self, BinningAppliedMessage, self.__on_binning_applied)
        messenger.subscribe(self, RevertBinningMessage, self.__on_revert_binning)
        messenger.subscribe(self, DataChangedMessage, self.__on_data_changed)
        messenger.subscribe(self, GroupingModeChangedMessage, self.__on_grouping_mode_changed)

    def __variable_changed(self, variable: str):
        Manager.data.selected_variable = variable
        self.__assign_data()

    def __display_errors(self, state: bool):
        if Manager.data.binning_params.mode == BinningMode.INTERVALS:
            self.timelinePlotView.set_display_errors(state)
        else:
            self.barPlotView.set_display_errors(state)

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        self.ui.variableSelector.set_data(message.data.variables)
        self.__assign_data()

    def __on_clear_data(self, message: ClearDataMessage):
        self.ui.variableSelector.clear()
        if Manager.data.binning_params.mode == BinningMode.INTERVALS:
            self.timelinePlotView.clear_plot()
        else:
            self.barPlotView.clear_plot()

    def __on_binning_applied(self, message: BinningAppliedMessage):
        self.__assign_data()

    def __on_revert_binning(self, message: RevertBinningMessage):
        if Manager.data.binning_params.mode == BinningMode.INTERVALS:
            self.__assign_data()

    def __on_data_changed(self, message: DataChangedMessage):
        self.__assign_data()

    def __on_grouping_mode_changed(self, message: GroupingModeChangedMessage):
        self.__assign_data()

    def __assign_data(self):
        if Manager.data.selected_variable == "":
            return

        df = Manager.data.get_current_df(calculate_error=False, variables=[Manager.data.selected_variable])

        if Manager.data.binning_params.mode == BinningMode.INTERVALS:
            if Manager.data.binning_params.mode != self.active_binning_mode:
                self.ui.verticalLayout.replaceWidget(self.barPlotView, self.timelinePlotView)
                self.barPlotView.hide()
                self.timelinePlotView.show()
                self.active_binning_mode = Manager.data.binning_params.mode
            self.timelinePlotView.set_variable(Manager.data.selected_variable, False)
            self.timelinePlotView.set_data(df)
        else:
            if Manager.data.binning_params.mode != self.active_binning_mode:
                self.ui.verticalLayout.replaceWidget(self.timelinePlotView, self.barPlotView)
                self.timelinePlotView.hide()
                self.barPlotView.show()
                self.active_binning_mode = Manager.data.binning_params.mode
            self.barPlotView.set_variable(Manager.data.selected_variable, False)
            self.barPlotView.set_data(df)
