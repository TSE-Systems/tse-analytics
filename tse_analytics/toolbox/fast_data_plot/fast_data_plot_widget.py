from dataclasses import dataclass

from matplotlib.backends.backend_qt import NavigationToolbar2QT
from PySide6.QtCore import QSettings, QSize, Qt
from PySide6.QtWidgets import QCheckBox, QInputDialog, QLabel, QToolBar, QVBoxLayout, QWidget

from tse_analytics.core import manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.grouping import GroupingSettings
from tse_analytics.core.data.operators.group_by_pipe_operator import group_by_columns
from tse_analytics.core.data.report import Report
from tse_analytics.core.data.shared import Variable
from tse_analytics.core.utils import get_h_spacer_widget
from tse_analytics.toolbox.fast_data_plot.bar_plot_view import BarPlotView
from tse_analytics.toolbox.fast_data_plot.timeline_plot_view import TimelinePlotView
from tse_analytics.toolbox.toolbox_registry import toolbox_plugin
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class FastDataPlotWidgetSettings:
    group_by: str = "Animal"
    selected_variable: str = None
    scatter_plot: bool = False


@toolbox_plugin(category="Data", label="Fast Plot", icon=":/icons/plot.png", order=1)
class FastDataPlotWidget(QWidget):
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
        self.add_report_action = toolbar.addAction("Add Report")
        self.add_report_action.triggered.connect(self._add_report)

        self._refresh_data()

    def _destroyed(self):
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

    def _refresh_data(self):
        grouping_settings = self.group_by_selector.get_grouping_settings()
        selected_variable = self.variableSelector.get_selected_variable()

        if "Timedelta" in self.datatable.df.columns:
            self._display_timeline_plot(
                selected_variable,
                grouping_settings,
            )
        else:
            self._display_bar_plot(
                selected_variable,
                grouping_settings,
                True,
            )

    def _display_timeline_plot(
        self,
        selected_variable: Variable,
        grouping_settings: GroupingSettings,
    ):
        self.barPlotView.hide()
        self.plot_toolbar_action.setVisible(False)
        self.timelinePlotView.show()
        self.checkBoxScatterPlot.setVisible(True)

        columns = self.datatable.get_default_columns() + list(self.datatable.dataset.factors) + [selected_variable.name]
        df = self.datatable.get_filtered_df(columns)

        df = group_by_columns(df, {selected_variable.name: selected_variable}, grouping_settings)

        self.timelinePlotView.refresh_data(
            self.datatable,
            df,
            selected_variable,
            grouping_settings,
            self.checkBoxScatterPlot.isChecked(),
        )

    def _display_bar_plot(
        self,
        selected_variable: Variable,
        grouping_settings: GroupingSettings,
        display_errors: bool,
    ):
        self.timelinePlotView.hide()
        self.barPlotView.show()
        self.plot_toolbar_action.setVisible(True)
        self.checkBoxScatterPlot.setVisible(False)

        if display_errors:
            error_type = "se"
        else:
            error_type = None

        columns = self.datatable.get_default_columns() + list(self.datatable.dataset.factors) + [selected_variable.name]
        df = self.datatable.get_filtered_df(columns)

        self.barPlotView.refresh_data(
            self.datatable,
            df,
            selected_variable,
            grouping_settings,
            display_errors,
            error_type,
        )

    def _add_report(self):
        if "Timedelta" in self.datatable.df.columns:
            html = self.timelinePlotView.get_report()
        else:
            html = self.barPlotView.get_report()

        name, ok = QInputDialog.getText(
            self,
            "Report",
            "Please enter report name:",
            text=self.title,
        )
        if ok and name:
            manager.add_report(
                Report(
                    self.datatable.dataset,
                    name,
                    html,
                )
            )
