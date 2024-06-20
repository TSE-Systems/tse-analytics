from matplotlib.backends.backend_qt import NavigationToolbar2QT
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget

from tse_analytics.core.data.binning import BinningMode
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import (
    BinningMessage,
    DataChangedMessage,
    DatasetChangedMessage,
)
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.messaging.messenger_listener import MessengerListener
from tse_analytics.views.data.bar_plot_view import BarPlotView
from tse_analytics.views.data.data_plot_widget_ui import Ui_DataPlotWidget
from tse_analytics.views.data.timeline_plot_view import TimelinePlotView
from tse_analytics.views.misc.toast import Toast


class DataPlotWidget(QWidget, MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_DataPlotWidget()
        self.ui.setupUi(self)

        self.register_to_messenger(Manager.messenger)

        self.ui.radioButtonSplitTotal.toggled.connect(self.__split_mode_changed)
        self.ui.radioButtonSplitByAnimal.toggled.connect(self.__split_mode_changed)
        self.ui.radioButtonSplitByFactor.toggled.connect(self.__split_mode_changed)
        self.ui.radioButtonSplitByRun.toggled.connect(self.__split_mode_changed)

        self.ui.variableSelector.currentTextChanged.connect(self.__variable_changed)
        self.ui.factorSelector.currentTextChanged.connect(self.__split_mode_changed)
        self.ui.checkBoxScatterPlot.stateChanged.connect(self.__set_scatter_plot)
        self.ui.groupBoxDisplayErrors.toggled.connect(self.__display_errors)
        self.ui.radioButtonStandardDeviation.toggled.connect(lambda: self.__error_type_changed("StandardDeviation"))
        self.ui.radioButtonStandardError.toggled.connect(lambda: self.__error_type_changed("StandardError"))

        self.timelinePlotView = TimelinePlotView(self)
        self.barPlotView = BarPlotView(self)

        self.ui.splitter.replaceWidget(0, self.timelinePlotView)
        self.active_binning_mode = BinningMode.INTERVALS

        self.plot_toolbar = NavigationToolbar2QT(self.barPlotView.canvas, self)
        self.plot_toolbar.setIconSize(QSize(16, 16))
        self.ui.widgetSettings.layout().addWidget(self.plot_toolbar)
        self.plot_toolbar.hide()

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)
        messenger.subscribe(self, BinningMessage, self.__on_binning_applied)
        messenger.subscribe(self, DataChangedMessage, self.__on_data_changed)

    def __variable_changed(self, variable: str):
        self.__assign_data()

    def __error_type_changed(self, error_type: str):
        if Manager.data.binning_params.mode == BinningMode.INTERVALS:
            self.timelinePlotView.set_error_type("std" if error_type == "StandardDeviation" else "sem")
        else:
            self.barPlotView.set_error_type("sd" if error_type == "StandardDeviation" else "se")

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
            self.ui.factorSelector.clear()
            if Manager.data.binning_params.mode == BinningMode.INTERVALS:
                self.timelinePlotView.clear_plot()
            else:
                self.barPlotView.clear_plot()
        else:
            self.ui.variableSelector.set_data(message.data.variables)
            self.ui.factorSelector.set_data(message.data.factors, add_empty_item=False)
            self.__assign_data()

    def __on_binning_applied(self, message: BinningMessage):
        if message.params.apply:
            self.__assign_data()
        else:
            if Manager.data.binning_params.mode == BinningMode.INTERVALS:
                self.__assign_data()

    def __on_data_changed(self, message: DataChangedMessage):
        self.__assign_data()

    def __split_mode_changed(self):
        selected_factor_name = self.ui.factorSelector.currentText()

        split_mode = SplitMode.TOTAL
        if self.ui.radioButtonSplitByAnimal.isChecked():
            split_mode = SplitMode.ANIMAL
        elif self.ui.radioButtonSplitByRun.isChecked():
            split_mode = SplitMode.RUN
        elif self.ui.radioButtonSplitByFactor.isChecked():
            split_mode = SplitMode.FACTOR

        self.ui.factorSelector.setEnabled(split_mode == SplitMode.FACTOR)

        factor = Manager.data.selected_dataset.factors[selected_factor_name] if selected_factor_name != "" else None
        self.timelinePlotView.set_grouping_mode(split_mode, factor)
        self.barPlotView.set_grouping_mode(split_mode, factor)
        self.__assign_data()

    def __assign_data(self):
        selected_factor_name = self.ui.factorSelector.currentText()

        split_mode = SplitMode.TOTAL
        if self.ui.radioButtonSplitByAnimal.isChecked():
            split_mode = SplitMode.ANIMAL
        elif self.ui.radioButtonSplitByRun.isChecked():
            split_mode = SplitMode.RUN
        elif self.ui.radioButtonSplitByFactor.isChecked():
            split_mode = SplitMode.FACTOR

        if split_mode == SplitMode.FACTOR and selected_factor_name == "":
            Toast(text="Please select factor.", parent=self, duration=2000).show_toast()
            return

        selected_variable = self.ui.variableSelector.currentText()

        df = (
            Manager.data.get_data_view_df(
                variables=[selected_variable],
                split_mode=split_mode,
                selected_factor=selected_factor_name
            )
            if Manager.data.binning_params.mode == BinningMode.INTERVALS
            else Manager.data.get_bar_plot_df(variable=selected_variable)
        )

        if Manager.data.binning_params.mode == BinningMode.INTERVALS:
            if Manager.data.binning_params.mode != self.active_binning_mode:
                self.ui.splitter.replaceWidget(0, self.timelinePlotView)
                self.barPlotView.hide()
                self.timelinePlotView.show()
                self.active_binning_mode = Manager.data.binning_params.mode
            self.timelinePlotView.set_variable(selected_variable, False)
            self.timelinePlotView.set_data(df)
            self.plot_toolbar.hide()
            self.ui.checkBoxScatterPlot.show()
        else:
            if Manager.data.binning_params.mode != self.active_binning_mode:
                self.ui.splitter.replaceWidget(0, self.barPlotView)
                self.timelinePlotView.hide()
                self.barPlotView.show()
                self.active_binning_mode = Manager.data.binning_params.mode
            self.barPlotView.set_variable(selected_variable, False)
            self.barPlotView.set_data(df)

            self.ui.checkBoxScatterPlot.hide()
            new_toolbar = NavigationToolbar2QT(self.barPlotView.canvas, self)
            new_toolbar.setIconSize(QSize(16, 16))
            self.plot_toolbar.hide()
            self.ui.widgetSettings.layout().replaceWidget(self.plot_toolbar, new_toolbar)
            self.plot_toolbar.deleteLater()
            self.plot_toolbar = new_toolbar
