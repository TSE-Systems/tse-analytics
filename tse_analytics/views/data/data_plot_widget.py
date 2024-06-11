from matplotlib.backends.backend_qt import NavigationToolbar2QT
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget

from tse_analytics.core.data.binning import BinningMode
from tse_analytics.core.data.shared import GroupingMode
from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import (
    BinningMessage,
    DataChangedMessage,
    DatasetChangedMessage,
    GroupingModeChangedMessage,
)
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.messaging.messenger_listener import MessengerListener
from tse_analytics.views.data.bar_plot_view import BarPlotView
from tse_analytics.views.data.data_plot_widget_ui import Ui_DataPlotWidget
from tse_analytics.views.data.timeline_plot_view import TimelinePlotView


class DataPlotWidget(QWidget, MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_DataPlotWidget()
        self.ui.setupUi(self)

        self.register_to_messenger(Manager.messenger)

        self.ui.comboBoxErrorType.addItems(["Standard deviation", "Standard error"])
        self.ui.comboBoxErrorType.setCurrentText("Standard deviation")
        self.ui.comboBoxErrorType.currentTextChanged.connect(self.__error_type_changed)

        self.ui.variableSelector.currentTextChanged.connect(self.__variable_changed)
        self.ui.toolButtonDisplayErrors.toggled.connect(self.__display_errors)
        self.ui.checkBoxScatterPlot.stateChanged.connect(self.__set_scatter_plot)

        self.timelinePlotView = TimelinePlotView(self)
        self.barPlotView = BarPlotView(self)

        self.ui.verticalLayout.addWidget(self.timelinePlotView)
        self.active_binning_mode = BinningMode.INTERVALS

        self.plotToolbar = NavigationToolbar2QT(self.barPlotView.canvas, self)
        self.plotToolbar.setIconSize(QSize(16, 16))
        self.ui.horizontalLayout.addWidget(self.plotToolbar)
        self.plotToolbar.hide()

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)
        messenger.subscribe(self, BinningMessage, self.__on_binning_applied)
        messenger.subscribe(self, DataChangedMessage, self.__on_data_changed)
        messenger.subscribe(self, GroupingModeChangedMessage, self.__on_grouping_mode_changed)

    def __variable_changed(self, variable: str):
        Manager.data.selected_variable = variable
        self.__assign_data()

    def __error_type_changed(self, error_type: str):
        if Manager.data.binning_params.mode == BinningMode.INTERVALS:
            self.timelinePlotView.set_error_type("std" if error_type == "Standard deviation" else "sem")
        else:
            self.barPlotView.set_error_type("sd" if error_type == "Standard deviation" else "se")

    def __display_errors(self, state: bool):
        if Manager.data.binning_params.mode == BinningMode.INTERVALS:
            self.timelinePlotView.set_display_errors(state)
        else:
            self.barPlotView.set_display_errors(state)

    def __set_scatter_plot(self, state: bool):
        self.timelinePlotView.set_scatter_plot(state)

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        if message.data is None:
            self.ui.variableSelector.clear()
            if Manager.data.binning_params.mode == BinningMode.INTERVALS:
                self.timelinePlotView.clear_plot()
            else:
                self.barPlotView.clear_plot()
        else:
            self.ui.variableSelector.set_data(message.data.variables)
            self.__assign_data()

    def __on_binning_applied(self, message: BinningMessage):
        if message.params.apply:
            self.__assign_data()
        else:
            if Manager.data.binning_params.mode == BinningMode.INTERVALS:
                self.__assign_data()

    def __on_data_changed(self, message: DataChangedMessage):
        self.__assign_data()

    def __on_grouping_mode_changed(self, message: GroupingModeChangedMessage):
        self.__assign_data()

    def __assign_data(self):
        if Manager.data.selected_variable == "" or (
            Manager.data.grouping_mode == GroupingMode.FACTORS and Manager.data.selected_factor is None
        ):
            return

        df = (
            Manager.data.get_data_view_df(variables=[Manager.data.selected_variable])
            if Manager.data.binning_params.mode == BinningMode.INTERVALS
            else Manager.data.get_bar_plot_df(variable=Manager.data.selected_variable)
        )

        if Manager.data.binning_params.mode == BinningMode.INTERVALS:
            if Manager.data.binning_params.mode != self.active_binning_mode:
                self.ui.verticalLayout.replaceWidget(self.barPlotView, self.timelinePlotView)
                self.barPlotView.hide()
                self.timelinePlotView.show()
                self.active_binning_mode = Manager.data.binning_params.mode
            self.timelinePlotView.set_variable(Manager.data.selected_variable, False)
            self.timelinePlotView.set_data(df)
            self.plotToolbar.hide()
            self.ui.checkBoxScatterPlot.show()
        else:
            if Manager.data.binning_params.mode != self.active_binning_mode:
                self.ui.verticalLayout.replaceWidget(self.timelinePlotView, self.barPlotView)
                self.timelinePlotView.hide()
                self.barPlotView.show()
                self.active_binning_mode = Manager.data.binning_params.mode
            self.barPlotView.set_variable(Manager.data.selected_variable, False)
            self.barPlotView.set_data(df)

            self.ui.checkBoxScatterPlot.hide()
            new_toolbar = NavigationToolbar2QT(self.barPlotView.canvas, self)
            new_toolbar.setIconSize(QSize(16, 16))
            self.plotToolbar.hide()
            self.ui.horizontalLayout.replaceWidget(self.plotToolbar, new_toolbar)
            self.plotToolbar.deleteLater()
            self.plotToolbar = new_toolbar
