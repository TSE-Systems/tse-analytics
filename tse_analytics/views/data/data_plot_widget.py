from matplotlib.backends.backend_qt import NavigationToolbar2QT
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget

from tse_analytics.core.data.binning import BinningMode
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import (
    AddToReportMessage,
    BinningMessage,
    DataChangedMessage,
    DatasetChangedMessage,
)
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.messaging.messenger_listener import MessengerListener
from tse_analytics.views.data.bar_plot_view import BarPlotView
from tse_analytics.views.data.data_plot_widget_ui import Ui_DataPlotWidget
from tse_analytics.views.data.timeline_plot_view import TimelinePlotView
from tse_analytics.views.misc.notification import Notification


class DataPlotWidget(QWidget, MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_DataPlotWidget()
        self.ui.setupUi(self)

        self.register_to_messenger(Manager.messenger)

        self.ui.radioButtonSplitTotal.toggled.connect(self._split_mode_toggled)
        self.ui.radioButtonSplitByAnimal.toggled.connect(self._split_mode_toggled)
        self.ui.radioButtonSplitByFactor.toggled.connect(self._split_mode_toggled)
        self.ui.radioButtonSplitByRun.toggled.connect(self._split_mode_toggled)

        self.ui.variableSelector.currentTextChanged.connect(self._variable_changed)
        # self.ui.factorSelector.currentTextChanged.connect(self._split_mode_changed)
        self.ui.factorSelector.currentTextChanged.connect(self._factor_changed)
        self.ui.checkBoxScatterPlot.stateChanged.connect(self._set_scatter_plot)
        self.ui.groupBoxDisplayErrors.toggled.connect(self._display_errors_toggled)
        self.ui.radioButtonStandardDeviation.toggled.connect(self._error_type_std_toggled)
        self.ui.radioButtonStandardError.toggled.connect(self._error_type_ste_toggled)

        self.ui.pushButtonAddReport.clicked.connect(self._add_report)

        self.timelinePlotView = TimelinePlotView(self)
        self.barPlotView = BarPlotView(self)

        self.ui.splitter.replaceWidget(0, self.timelinePlotView)
        self.active_binning_mode = BinningMode.INTERVALS

        self.plot_toolbar = NavigationToolbar2QT(self.barPlotView.canvas, self)
        self.plot_toolbar.setIconSize(QSize(16, 16))
        self.ui.widgetSettings.layout().addWidget(self.plot_toolbar)
        self.plot_toolbar.hide()

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self._on_dataset_changed)
        messenger.subscribe(self, BinningMessage, self._on_binning_applied)
        messenger.subscribe(self, DataChangedMessage, self._on_data_changed)

    def _variable_changed(self, variable: str):
        self._assign_data()

    def _factor_changed(self, factor_name: str):
        self._assign_data()

    def _error_type_std_toggled(self, toggled: bool):
        if not toggled:
            return
        if Manager.data.binning_params.mode == BinningMode.INTERVALS:
            self.timelinePlotView.set_error_type("std")
        else:
            self.barPlotView.set_error_type("sd")

    def _error_type_ste_toggled(self, toggled: bool):
        if not toggled:
            return
        if Manager.data.binning_params.mode == BinningMode.INTERVALS:
            self.timelinePlotView.set_error_type("sem")
        else:
            self.barPlotView.set_error_type("se")

    def _display_errors_toggled(self, toggled: bool):
        if Manager.data.binning_params.mode == BinningMode.INTERVALS:
            self.timelinePlotView.set_display_errors(toggled)
        else:
            self.barPlotView.set_display_errors(toggled)

    def _set_scatter_plot(self, state: bool):
        self.timelinePlotView.set_scatter_plot(state)

    def _on_dataset_changed(self, message: DatasetChangedMessage):
        self.ui.pushButtonAddReport.setDisabled(message.data is None)
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
            self._assign_data()

    def _on_binning_applied(self, message: BinningMessage):
        if message.params.apply:
            self._assign_data()
        else:
            if Manager.data.binning_params.mode == BinningMode.INTERVALS:
                self._assign_data()

    def _on_data_changed(self, message: DataChangedMessage):
        self._assign_data()

    def _split_mode_toggled(self, toggled: bool):
        if not toggled:
            return

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
        self._assign_data()

    def _assign_data(self):
        if Manager.data.selected_dataset is None:
            return

        selected_factor_name = self.ui.factorSelector.currentText()

        split_mode = SplitMode.TOTAL
        if self.ui.radioButtonSplitByAnimal.isChecked():
            split_mode = SplitMode.ANIMAL
        elif self.ui.radioButtonSplitByRun.isChecked():
            split_mode = SplitMode.RUN
        elif self.ui.radioButtonSplitByFactor.isChecked():
            split_mode = SplitMode.FACTOR

        if split_mode == SplitMode.FACTOR and selected_factor_name == "":
            Notification(text="Please select factor.", parent=self, duration=2000).show_notification()
            return

        selected_variable = self.ui.variableSelector.currentText()

        df = (
            Manager.data.get_data_view_df(
                variables=[selected_variable], split_mode=split_mode, selected_factor=selected_factor_name
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

    def _add_report(self):
        html = (
            self.timelinePlotView.get_report()
            if Manager.data.binning_params.mode == BinningMode.INTERVALS
            else self.barPlotView.get_report()
        )
        Manager.messenger.broadcast(AddToReportMessage(self, html))
