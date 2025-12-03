from dataclasses import dataclass

import pandas as pd
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from pyqttoast import ToastPreset
from PySide6.QtCore import QSettings, QSize, Qt
from PySide6.QtWidgets import QCheckBox, QLabel, QToolBar, QVBoxLayout, QWidget

from tse_analytics.core import manager, messaging
from tse_analytics.core.data.binning import BinningMode
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.pipeline.time_cycles_binning_pipe_operator import process_time_cycles_binning
from tse_analytics.core.data.pipeline.time_intervals_binning_pipe_operator import process_time_interval_binning
from tse_analytics.core.data.pipeline.time_phases_binning_pipe_operator import process_time_phases_binning
from tse_analytics.core.data.report import Report
from tse_analytics.core.data.shared import SplitMode, Variable
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_h_spacer_widget
from tse_analytics.toolbox.fast_data_plot.bar_plot_view import BarPlotView
from tse_analytics.toolbox.fast_data_plot.timeline_plot_view import TimelinePlotView
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class FastDataPlotWidgetSettings:
    group_by: str = "Animal"
    selected_variable: str = None
    scatter_plot: bool = False


class FastDataPlotWidget(QWidget, messaging.MessengerListener):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        # Connect destructor to unsubscribe and save settings
        self.destroyed.connect(lambda: self._destroyed())

        # Settings management
        settings = QSettings()
        self._settings: FastDataPlotWidgetSettings = settings.value(
            self.__class__.__name__, FastDataPlotWidgetSettings()
        )

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Fast Plot"

        self.datatable = datatable

        # Setup toolbar
        toolbar = QToolBar(
            "Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        self.variableSelector = VariableSelector(toolbar)
        self.variableSelector.set_data(self.datatable.variables, selected_variable=self._settings.selected_variable)
        self.variableSelector.currentTextChanged.connect(self._variable_changed)
        toolbar.addWidget(self.variableSelector)

        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Group by:"))
        self.group_by_selector = GroupBySelector(
            toolbar,
            self.datatable,
            check_binning=True,
            selected_mode=self._settings.group_by,
        )
        self.group_by_selector.currentTextChanged.connect(self._refresh_data)
        toolbar.addWidget(self.group_by_selector)

        self.checkBoxScatterPlot = QCheckBox("Scatter Plot", toolbar)
        self.checkBoxScatterPlot.setChecked(self._settings.scatter_plot)
        self.checkBoxScatterPlot.checkStateChanged.connect(self._set_scatter_plot)
        toolbar.addWidget(self.checkBoxScatterPlot)

        # Insert toolbar to the widget
        self._layout.addWidget(toolbar)

        self.timelinePlotView = TimelinePlotView(self)
        self._layout.addWidget(self.timelinePlotView)

        self.barPlotView = BarPlotView(self)
        self.barPlotView.hide()
        self._layout.addWidget(self.barPlotView)

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

    def _destroyed(self):
        messaging.unsubscribe_all(self)
        settings = QSettings()
        settings.setValue(
            self.__class__.__name__,
            FastDataPlotWidgetSettings(
                self.group_by_selector.currentText(),
                self.variableSelector.currentText(),
                self.checkBoxScatterPlot.isChecked(),
            ),
        )

    def _variable_changed(self, variable: str) -> None:
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
        split_mode, selected_factor_name = self.group_by_selector.get_group_by()
        if split_mode == SplitMode.FACTOR and selected_factor_name == "":
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

        if not self.datatable.dataset.binning_settings.apply:
            self._display_timeline_plot(
                selected_variable,
                split_mode,
                selected_factor_name,
            )
        else:
            if self.datatable.dataset.binning_settings.mode == BinningMode.INTERVALS:
                self._display_timeline_plot(
                    selected_variable,
                    split_mode,
                    selected_factor_name,
                )
            else:
                self._display_bar_plot(
                    selected_variable,
                    split_mode,
                    selected_factor_name,
                    True,
                )

    def _get_timeline_plot_df(
        self,
        variable: Variable,
        split_mode: SplitMode,
        selected_factor_name: str,
    ) -> pd.DataFrame:
        columns = self.datatable.get_default_columns() + list(self.datatable.dataset.factors) + [variable.name]
        result = self.datatable.get_filtered_df(columns)

        # Binning
        settings = self.datatable.dataset.binning_settings
        if settings.apply:
            result = process_time_interval_binning(
                result,
                settings.time_intervals_settings,
                {variable.name: variable},
                origin=self.datatable.dataset.experiment_started,
            )

        # Splitting

        # No processing!
        if split_mode == SplitMode.ANIMAL:
            return result

        match split_mode:
            case SplitMode.FACTOR:
                by = ["Bin", selected_factor_name]
            case SplitMode.RUN:
                by = ["Bin", "Run"]
            case _:  # Total split mode
                by = ["Bin"]

        # TODO: use means only when aggregating in split modes!
        aggregation = {
            "Timedelta": "first",
            variable.name: "mean",
        }

        result = result.groupby(by, dropna=False, observed=False).aggregate(aggregation)
        result.reset_index(inplace=True)

        return result

    def _display_timeline_plot(
        self,
        selected_variable: Variable,
        split_mode: SplitMode,
        selected_factor_name: str,
    ):
        self.barPlotView.hide()
        self.plot_toolbar_action.setVisible(False)
        self.timelinePlotView.show()
        self.checkBoxScatterPlot.setVisible(True)

        df = self._get_timeline_plot_df(
            variable=selected_variable,
            split_mode=split_mode,
            selected_factor_name=selected_factor_name,
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
            selected_factor,
            self.checkBoxScatterPlot.isChecked(),
        )

    def _get_bar_plot_df(
        self,
        variable: Variable,
    ) -> pd.DataFrame:
        columns = self.datatable.get_default_columns() + list(self.datatable.dataset.factors) + [variable.name]
        result = self.datatable.get_filtered_df(columns)

        variables = {variable.name: variable}

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
            calculate_errors = "se"
        else:
            calculate_errors = None

        df = self._get_bar_plot_df(
            variable=selected_variable,
        )

        selected_factor = (
            self.datatable.dataset.factors[selected_factor_name]
            if split_mode == SplitMode.FACTOR and selected_factor_name != ""
            else None
        )

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

        manager.add_report(
            Report(
                self.datatable.dataset,
                self.title,
                html,
            )
        )
