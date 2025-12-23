from dataclasses import dataclass, field

import pandas as pd
import seaborn.objects as so
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from PySide6.QtCore import QSettings, QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QAbstractScrollArea,
    QComboBox,
    QDoubleSpinBox,
    QInputDialog,
    QLabel,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from tse_analytics.core import color_manager, manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.pipeline.time_intervals_binning_pipe_operator import process_time_interval_binning
from tse_analytics.core.data.report import Report
from tse_analytics.core.data.shared import SplitMode, Variable
from tse_analytics.core.utils import (
    get_h_spacer_widget,
    get_html_image_from_figure,
    get_widget_tool_button,
    time_to_float,
)
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.variables_table_widget import VariablesTableWidget


@dataclass
class DataPlotWidgetSettings:
    group_by: str = "Animal"
    selected_variables: list[str] = field(default_factory=list)
    error_bar: str = "Standard Error"
    line_width: float = 1.0


class DataPlotWidget(QWidget):
    error_bar = {
        "None": None,
        "Confidence Interval": "ci",
        "Percentile Interval": "pi",
        "Standard Error": "se",
        "Standard Deviation": "sd",
    }

    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        # Connect destructor to unsubscribe and save settings
        self.destroyed.connect(lambda: self._destroyed())

        # Settings management
        settings = QSettings()
        self._settings: DataPlotWidgetSettings = settings.value(self.__class__.__name__, DataPlotWidgetSettings())

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Plot"

        self.datatable = datatable

        # Setup toolbar
        toolbar = QToolBar(
            "Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        toolbar.addAction(QIcon(":/icons/icons8-refresh-16.png"), "Update").triggered.connect(self._update)
        toolbar.addSeparator()

        self.variables_table_widget = VariablesTableWidget()
        self.variables_table_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.variables_table_widget.set_data(self.datatable.variables, self._settings.selected_variables)
        self.variables_table_widget.setMaximumHeight(600)
        self.variables_table_widget.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        variables_button = get_widget_tool_button(
            toolbar,
            self.variables_table_widget,
            "Variables",
            QIcon(":/icons/variables.png"),
        )
        toolbar.addWidget(variables_button)

        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Group by:"))
        self.group_by_selector = GroupBySelector(toolbar, self.datatable, selected_mode=self._settings.group_by)
        toolbar.addWidget(self.group_by_selector)

        toolbar.addWidget(QLabel("Error Bar:"))
        self.comboBoxErrorBar = QComboBox(toolbar)
        self.comboBoxErrorBar.addItems(DataPlotWidget.error_bar.keys())
        self.comboBoxErrorBar.setCurrentText(self._settings.error_bar)
        toolbar.addWidget(self.comboBoxErrorBar)

        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Line Width:"))
        self.linewidth_spin_box = QDoubleSpinBox(
            toolbar,
            minimum=0,
            maximum=3,
            singleStep=0.5,
            value=self._settings.line_width,
        )
        toolbar.addWidget(self.linewidth_spin_box)

        # Insert the toolbar to the widget
        self._layout.addWidget(toolbar)

        self.canvas = MplCanvas(self)
        self._layout.addWidget(self.canvas)

        plot_toolbar = NavigationToolbar2QT(self.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        toolbar.addWidget(plot_toolbar)

        toolbar.addWidget(get_h_spacer_widget(toolbar))
        toolbar.addAction("Add Report").triggered.connect(self._add_report)

    def _destroyed(self):
        settings = QSettings()
        settings.setValue(
            self.__class__.__name__,
            DataPlotWidgetSettings(
                self.group_by_selector.currentText(),
                self.variables_table_widget.get_selected_variable_names(),
                self.comboBoxErrorBar.currentText(),
                self.linewidth_spin_box.value(),
            ),
        )

    def _update(self):
        # Clear the plot
        self.canvas.clear(False)

        selected_variables_dict = self.variables_table_widget.get_selected_variables_dict()
        if len(selected_variables_dict) == 0:
            return

        split_mode, selected_factor_name = self.group_by_selector.get_group_by()
        error_bar = DataPlotWidget.error_bar[self.comboBoxErrorBar.currentText()]

        match split_mode:
            case SplitMode.ANIMAL:
                by = "Animal"
                palette = color_manager.get_animal_to_color_dict(self.datatable.dataset.animals)
            case SplitMode.RUN:
                by = "Run"
                palette = color_manager.colormap_name
            case SplitMode.FACTOR:
                by = selected_factor_name
                palette = color_manager.get_level_to_color_dict(self.datatable.dataset.factors[selected_factor_name])
            case _:
                by = None
                palette = color_manager.colormap_name

        df = self._get_timeline_plot_df(selected_variables_dict)

        (
            so
            .Plot(
                df,
                x="Hours",
                color=by,
            )
            .pair(y=list(selected_variables_dict))
            .add(so.Line(linewidth=self.linewidth_spin_box.value()), so.Agg(func="mean"))  # Line with mean estimate
            .add(so.Band(alpha=0.15), so.Est(errorbar=error_bar))  # Shaded CI band
            .scale(color=palette)
            .on(self.canvas.figure)
            .plot(True)
        )

        # Draw light/dark bands
        if True:
            settings = self.datatable.dataset.binning_settings.time_cycles_settings

            dark_start = time_to_float(settings.dark_cycle_start)
            dark_end = time_to_float(settings.light_cycle_start)
            dark_duration = abs(dark_end - dark_start)
            max_hours = df["Hours"].max()

            experiment_started_time = time_to_float(self.datatable.dataset.experiment_started.time())
            time_shift = abs(experiment_started_time - dark_start)
            start = time_shift
            while start < max_hours:
                for ax in self.canvas.figure.axes:
                    ax.axvspan(start, start + dark_duration, color="gray", alpha=0.15)
                start = 24 + start

        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def _get_timeline_plot_df(
        self,
        variables: dict[str, Variable],
    ) -> pd.DataFrame:
        columns = self.datatable.get_default_columns() + list(self.datatable.dataset.factors) + list(variables)
        result = self.datatable.get_filtered_df(columns)

        # Binning
        settings = self.datatable.dataset.binning_settings
        if settings.apply:
            result = process_time_interval_binning(
                result,
                settings.time_intervals_settings,
                variables,
                origin=self.datatable.dataset.experiment_started,
            )

        result["Hours"] = result["Timedelta"] / pd.Timedelta(1, "h")

        return result

    def _add_report(self) -> None:
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
                    get_html_image_from_figure(self.canvas.figure),
                )
            )
