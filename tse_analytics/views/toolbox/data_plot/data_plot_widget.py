import pandas as pd
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar, QCheckBox, QComboBox, QLabel
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from pyqttoast import ToastPreset

from tse_analytics.core import messaging
from tse_analytics.core.data.binning import BinningMode
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.pipeline.time_cycles_binning_pipe_operator import process_time_cycles_binning
from tse_analytics.core.data.pipeline.time_intervals_binning_pipe_operator import process_time_interval_binning
from tse_analytics.core.data.pipeline.time_phases_binning_pipe_operator import process_time_phases_binning
from tse_analytics.core.data.shared import SplitMode, Variable
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_h_spacer_widget
from tse_analytics.views.toolbox.data_plot.bar_plot_view import BarPlotView
from tse_analytics.views.toolbox.data_plot.timeline_plot_view import TimelinePlotView
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.variable_selector import VariableSelector


class DataPlotWidget(QWidget, messaging.MessengerListener):
    """Widget for visualizing data in different plot formats.

    This widget provides functionality for visualizing data from a datatable
    in different plot formats (timeline plot and bar plot) based on the selected
    variable and grouping options. It supports various visualization options
    like error bars, scatter plots, and different binning modes.

    Attributes:
        datatable: The datatable containing the data to visualize.
        split_mode: The mode for splitting/grouping the data (by animal, factor, run, or total).
        selected_factor_name: The name of the selected factor when split_mode is FACTOR.
        variableSelector: Selector for choosing which variable to visualize.
        group_by_selector: Selector for choosing how to group the data.
        checkBoxScatterPlot: Checkbox for enabling/disabling scatter plot.
        checkBoxDisplayErrors: Checkbox for enabling/disabling error bars.
        error_type_combobox: Combobox for selecting the type of error (SE or SD).
        timelinePlotView: View for displaying timeline plots.
        barPlotView: View for displaying bar plots.
    """

    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        """Initialize the data plot widget.

        Args:
            datatable: The datatable containing the data to visualize.
            parent: The parent widget, if any.
        """
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

        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Group by:"))
        self.group_by_selector = GroupBySelector(toolbar, self.datatable, self._group_by_callback)
        toolbar.addWidget(self.group_by_selector)

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

    def _group_by_callback(self, mode: SplitMode, factor_name: str | None):
        """Handle changes in the group by selector.

        Args:
            mode: The selected split mode (ANIMAL, FACTOR, RUN, TOTAL).
            factor_name: The name of the selected factor when mode is FACTOR.
        """
        self.split_mode = mode
        self.selected_factor_name = factor_name
        self._refresh_data()

    def _variable_changed(self, variable: str) -> None:
        """Handle changes in the variable selector.

        Args:
            variable: The name of the selected variable.
        """
        self._refresh_data()

    def _error_type_changed(self, text: str):
        """Handle changes in the error type combobox.

        Args:
            text: The selected error type ("Standard Error" or "Standard Deviation").
        """
        self._refresh_data()

    def _display_errors_changed(self, state: Qt.CheckState) -> None:
        """Handle changes in the display errors checkbox.

        Args:
            state: The new state of the checkbox.
        """
        self.error_type_action.setVisible(state == Qt.CheckState.Checked)
        self._refresh_data()

    def _set_scatter_plot(self, state: Qt.CheckState):
        """Handle changes in the scatter plot checkbox.

        Args:
            state: The new state of the checkbox.
        """
        self._refresh_data()

    def _on_binning_applied(self, message: messaging.BinningMessage):
        """Handle binning applied messages.

        Refreshes the data when binning settings are changed for the current dataset.

        Args:
            message: The binning message containing the affected dataset.
        """
        if message.dataset == self.datatable.dataset:
            self._refresh_data()

    def _on_data_changed(self, message: messaging.DataChangedMessage):
        """Handle data changed messages.

        Refreshes the data when the current dataset is modified.

        Args:
            message: The data changed message containing the affected dataset.
        """
        if message.dataset == self.datatable.dataset:
            self._refresh_data()

    def _refresh_data(self):
        """Refresh the data visualization based on current settings.

        This method determines which type of plot to display (timeline or bar)
        based on the current binning settings and updates the visualization
        with the selected variable and grouping options.
        """
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
                    selected_variable,
                    self.split_mode,
                    self.selected_factor_name,
                    display_errors,
                )
            else:
                self._display_bar_plot(
                    selected_variable,
                    self.split_mode,
                    self.selected_factor_name,
                    display_errors,
                )

    def _get_timeline_plot_df(
        self,
        variable: Variable,
        split_mode: SplitMode,
        selected_factor_name: str,
        calculate_errors: str | None,
    ) -> pd.DataFrame:
        """Process data for timeline plot visualization.

        This method retrieves the data for the selected variable, applies time interval
        binning if enabled, and performs grouping based on the selected split mode.

        Args:
            variable: The variable to visualize.
            split_mode: The mode for splitting/grouping the data.
            selected_factor_name: The name of the selected factor when split_mode is FACTOR.
            calculate_errors: The type of error to calculate ("sem", "std", or None).

        Returns:
            A DataFrame containing the processed data for timeline plot visualization.
        """
        columns = self.datatable.get_default_columns() + list(self.datatable.dataset.factors) + [variable.name]
        result = self.datatable.get_filtered_df(columns)

        # Binning
        settings = self.datatable.dataset.binning_settings
        if settings.apply:
            result = process_time_interval_binning(
                result,
                settings.time_intervals_settings,
                {variable.name: variable},
                calculate_errors,
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

        # Calculate error for timeline plot
        if calculate_errors is not None:
            result["Error"] = result[variable.name]
            result["Error"] = calculate_errors

        result = result.groupby(by, dropna=False, observed=False).aggregate(aggregation)
        result.reset_index(inplace=True)

        return result

    def _display_timeline_plot(
        self,
        selected_variable: Variable,
        split_mode: SplitMode,
        selected_factor_name: str,
        display_errors: bool,
    ):
        """Display data in a timeline plot.

        This method processes the data and updates the timeline plot view
        with the selected variable, grouping options, and visualization settings.

        Args:
            selected_variable: The variable to visualize.
            split_mode: The mode for splitting/grouping the data.
            selected_factor_name: The name of the selected factor when split_mode is FACTOR.
            display_errors: Whether to display error bars.
        """
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
        """Process data for bar plot visualization.

        This method retrieves the data for the selected variable and applies
        appropriate binning (cycles or phases) based on the current binning settings.

        Args:
            variable: The variable to visualize.

        Returns:
            A DataFrame containing the processed data for bar plot visualization.
        """
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
        """Display data in a bar plot.

        This method processes the data and updates the bar plot view
        with the selected variable, grouping options, and visualization settings.

        Args:
            selected_variable: The variable to visualize.
            split_mode: The mode for splitting/grouping the data.
            selected_factor_name: The name of the selected factor when split_mode is FACTOR.
            display_errors: Whether to display error bars.
        """
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
        """Add the current plot to the dataset report.

        This method gets the HTML representation of the current plot
        (timeline or bar) and adds it to the dataset's report. It also
        broadcasts a message to notify the application that content
        has been added to the report.
        """
        if not self.datatable.dataset.binning_settings.apply:
            html = self.timelinePlotView.get_report()
        else:
            if self.datatable.dataset.binning_settings.mode == BinningMode.INTERVALS:
                html = self.timelinePlotView.get_report()
            else:
                html = self.barPlotView.get_report()
        self.datatable.dataset.report += html
        messaging.broadcast(messaging.AddToReportMessage(self, self.datatable.dataset))
