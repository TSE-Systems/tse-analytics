import pandas as pd
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar, QCheckBox, QComboBox
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from pyqttoast import ToastPreset

from tse_analytics.core import messaging
from tse_analytics.core.data.binning import BinningMode
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.pipeline.time_cycles_binning_pipe_operator import process_time_cycles_binning
from tse_analytics.core.data.pipeline.time_intervals_binning_pipe_operator import process_time_interval_binning
from tse_analytics.core.data.pipeline.time_phases_binning_pipe_operator import process_time_phases_binning
from tse_analytics.core.data.shared import SplitMode, Variable
from tse_analytics.core.utils import get_h_spacer_widget
from tse_analytics.core.toaster import make_toast
from tse_analytics.views.data.bar_plot_view import BarPlotView
from tse_analytics.views.data.timeline_plot_view import TimelinePlotView
from tse_analytics.views.misc.split_mode_selector import SplitModeSelector
from tse_analytics.views.misc.variable_selector import VariableSelector


class DataPlotWidget(QWidget, messaging.MessengerListener):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.datatable = datatable
        self.split_mode = SplitMode.ANIMAL
        self.selected_factor_name = ""

        # Setup toolbar
        toolbar = QToolBar(
            "Data Plot Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        self.variableSelector = VariableSelector(toolbar)
        self.variableSelector.set_data(self.datatable.variables)
        self.variableSelector.currentTextChanged.connect(self._variable_changed)
        toolbar.addWidget(self.variableSelector)

        self.split_mode_selector = SplitModeSelector(toolbar, self.datatable, self._split_mode_callback)
        toolbar.addWidget(self.split_mode_selector)

        self.checkBoxScatterPlot = QCheckBox("Scatter Plot", toolbar)
        self.checkBoxScatterPlot.checkStateChanged.connect(self._set_scatter_plot)
        toolbar.addWidget(self.checkBoxScatterPlot)

        self.checkBoxDisplayErrors = QCheckBox("Display Errors", toolbar)
        self.checkBoxDisplayErrors.checkStateChanged.connect(self._display_errors_changed)
        toolbar.addWidget(self.checkBoxDisplayErrors)

        self.error_type_combobox = QComboBox(toolbar)
        self.error_type_combobox.addItems(["Standard Error", "Standard Deviation"])
        self.error_type_combobox.currentTextChanged.connect(self._error_type_changed)
        self.error_type_action = toolbar.addWidget(self.error_type_combobox)
        self.error_type_action.setVisible(False)

        # Insert toolbar to the widget
        self.layout.addWidget(toolbar)

        self.timelinePlotView = TimelinePlotView(self)
        self.layout.addWidget(self.timelinePlotView)

        self.barPlotView = BarPlotView(self)
        self.barPlotView.hide()
        self.layout.addWidget(self.barPlotView)

        plot_toolbar = NavigationToolbar2QT(self.barPlotView.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        self.plot_toolbar_action = toolbar.addWidget(plot_toolbar)
        self.plot_toolbar_action.setVisible(False)

        toolbar.addWidget(get_h_spacer_widget(toolbar))
        self.add_report_action = toolbar.addAction("Add to Report")
        self.add_report_action.triggered.connect(self._add_report)

        self._refresh_data()

        messaging.subscribe(self, messaging.BinningMessage, self._on_binning_applied)
        messaging.subscribe(self, messaging.DataChangedMessage, self._on_data_changed)
        self.destroyed.connect(lambda: messaging.unsubscribe_all(self))

    def _split_mode_callback(self, mode: SplitMode, factor_name: str | None):
        self.split_mode = mode
        self.selected_factor_name = factor_name
        self._refresh_data()

    def _variable_changed(self, variable: str) -> None:
        self._refresh_data()

    def _error_type_changed(self, text: str):
        self._refresh_data()

    def _display_errors_changed(self, state: Qt.CheckState) -> None:
        self.error_type_action.setVisible(state == Qt.CheckState.Checked)
        self._refresh_data()

    def _set_scatter_plot(self, state: Qt.CheckState):
        self._refresh_data()

    def _on_binning_applied(self, message: messaging.BinningMessage):
        if message.dataset == self.datatable.dataset:
            self._refresh_data()

    def _on_data_changed(self, message: messaging.DataChangedMessage):
        if message.dataset == self.datatable.dataset:
            self._refresh_data()

    def _refresh_data(self):
        if self.split_mode == SplitMode.FACTOR and self.selected_factor_name == "":
            make_toast(
                self,
                "Data Plot",
                "Please select factor.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        selected_variable = self.variableSelector.get_selected_variable()
        display_errors = self.checkBoxDisplayErrors.isChecked()

        if not self.datatable.dataset.binning_settings.apply:
            self._display_timeline_plot(selected_variable, self.split_mode, self.selected_factor_name, display_errors)
        else:
            if self.datatable.dataset.binning_settings.mode == BinningMode.INTERVALS:
                self._display_timeline_plot(
                    selected_variable, self.split_mode, self.selected_factor_name, display_errors
                )
            else:
                self._display_bar_plot(selected_variable, self.split_mode, self.selected_factor_name, display_errors)

    def _get_timeline_plot_df(
        self,
        variable: Variable,
        split_mode: SplitMode,
        selected_factor_name: str,
        calculate_errors: str | None,
    ) -> pd.DataFrame:
        factor_columns = list(self.datatable.dataset.factors)
        result = self.datatable.active_df[
            self.datatable.get_default_columns() + factor_columns + [variable.name]
        ].copy()

        variables = {variable.name: variable}

        result = self.datatable.preprocess_df(result, variables)

        # Binning
        settings = self.datatable.dataset.binning_settings
        if settings.apply:
            # if split_mode == SplitMode.ANIMAL:
            #     calculate_errors = None
            result = process_time_interval_binning(
                result,
                settings.time_intervals_settings,
                variables,
                calculate_errors,
            )

        # Splitting
        result = self.datatable.process_splitting(
            result,
            split_mode,
            variables,
            selected_factor_name,
            calculate_errors,
        )

        return result

    def _display_timeline_plot(
        self,
        selected_variable: Variable,
        split_mode: SplitMode,
        selected_factor_name: str,
        display_errors: bool,
    ):
        self.barPlotView.hide()
        self.plot_toolbar_action.setVisible(False)
        self.timelinePlotView.show()
        self.checkBoxScatterPlot.setVisible(True)

        if display_errors:
            calculate_errors = "sem" if self.error_type_combobox.currentText() == "Standard Error" else "std"
        else:
            calculate_errors = None

        df = self._get_timeline_plot_df(
            variable=selected_variable,
            split_mode=split_mode,
            selected_factor_name=selected_factor_name,
            calculate_errors=calculate_errors,
        )

        selected_factor = (
            self.datatable.dataset.factors[selected_factor_name]
            if (selected_factor_name != "" and selected_factor_name in self.datatable.dataset.factors)
            else None
        )

        self.timelinePlotView.refresh_data(
            self.datatable,
            df,
            selected_variable,
            split_mode,
            display_errors,
            selected_factor,
            self.checkBoxScatterPlot.isChecked(),
        )

    def _get_bar_plot_df(
        self,
        variable: Variable,
    ) -> pd.DataFrame:
        factor_columns = list(self.datatable.dataset.factors)
        result = self.datatable.active_df[
            self.datatable.get_default_columns() + factor_columns + [variable.name]
        ].copy()

        variables = {variable.name: variable}

        result = self.datatable.preprocess_df(result, variables)

        settings = self.datatable.dataset.binning_settings
        match settings.mode:
            case BinningMode.CYCLES:
                result = process_time_cycles_binning(
                    result,
                    settings.time_cycles_settings,
                    variables,
                )
            case BinningMode.PHASES:
                result = process_time_phases_binning(
                    result,
                    settings.time_phases_settings,
                    variables,
                )

        return result

    def _display_bar_plot(
        self,
        selected_variable: Variable,
        split_mode: SplitMode,
        selected_factor_name: str,
        display_errors: bool,
    ):
        self.timelinePlotView.hide()
        self.barPlotView.show()
        self.plot_toolbar_action.setVisible(True)
        self.checkBoxScatterPlot.setVisible(False)

        if display_errors:
            calculate_errors = "se" if self.error_type_combobox.currentText() == "Standard Error" else "sd"
        else:
            calculate_errors = None

        df = self._get_bar_plot_df(
            variable=selected_variable,
        )

        selected_factor = self.datatable.dataset.factors[selected_factor_name] if selected_factor_name != "" else None

        self.barPlotView.refresh_data(
            self.datatable,
            df,
            selected_variable,
            split_mode,
            selected_factor,
            display_errors,
            calculate_errors,
        )

    def _add_report(self):
        if not self.datatable.dataset.binning_settings.apply:
            html = self.timelinePlotView.get_report()
        else:
            if self.datatable.dataset.binning_settings.mode == BinningMode.INTERVALS:
                html = self.timelinePlotView.get_report()
            else:
                html = self.barPlotView.get_report()
        self.datatable.dataset.report += html
        messaging.broadcast(messaging.AddToReportMessage(self, self.datatable.dataset))
