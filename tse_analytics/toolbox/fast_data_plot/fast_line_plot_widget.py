import base64
from dataclasses import dataclass
from io import BytesIO
from math import isnan

import pandas as pd
import pyqtgraph as pg
from pyqtgraph.exporters import ImageExporter
from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QSettings, QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QCheckBox, QInputDialog, QLabel, QToolBar, QVBoxLayout, QWidget

from tse_analytics.core import color_manager, manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.grouping import GroupingMode
from tse_analytics.core.data.operators.group_by_pipe_operator import group_by_columns
from tse_analytics.core.data.report import Report
from tse_analytics.core.data.shared import Factor
from tse_analytics.core.utils import get_h_spacer_widget, get_widget_tool_button
from tse_analytics.views.misc.animals_table_view import AnimalsTableView
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.TimedeltaAxisItem import TimedeltaAxisItem
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class FastLinePlotWidgetSettings:
    group_by: str = "Animal"
    selected_variable: str = None
    scatter_plot: bool = False


class FastLinePlotWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        # Connect destructor to unsubscribe and save settings
        self.destroyed.connect(lambda: self._destroyed())

        # Settings management
        settings = QSettings()
        self._settings: FastLinePlotWidgetSettings = settings.value(
            self.__class__.__name__, FastLinePlotWidgetSettings()
        )

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Fast Line Plot"

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
            selected_mode=self._settings.group_by,
        )
        self.group_by_selector.currentTextChanged.connect(self._refresh_data)
        toolbar.addWidget(self.group_by_selector)

        self.checkBoxScatterPlot = QCheckBox("Scatter Plot", toolbar)
        self.checkBoxScatterPlot.setChecked(self._settings.scatter_plot)
        self.checkBoxScatterPlot.checkStateChanged.connect(self._set_scatter_plot)
        toolbar.addWidget(self.checkBoxScatterPlot)

        self.animals_table_view = AnimalsTableView(self.datatable.dataset)
        self.animals_table_view.selectionModel().selectionChanged.connect(self._refresh_data)
        animals_button = get_widget_tool_button(
            toolbar,
            self.animals_table_view,
            "Animal Filter",
            QIcon(":/icons/icons8-rat-silhouette-16.png"),
        )
        toolbar.addWidget(animals_button)

        # Insert toolbar to the widget
        self._layout.addWidget(toolbar)

        self.plot_view = pg.GraphicsLayoutWidget(self, show=False, size=None, title=None)

        # Set layout proportions
        self.plot_view.ci.layout.setRowStretchFactor(0, 3)

        self.plot_item1 = self.plot_view.ci.addPlot(row=0, col=0)
        # self.plot_item1.setAxisItems({"bottom": pg.DateAxisItem(utcOffset=0)})
        self.plot_item1.setAxisItems({"bottom": TimedeltaAxisItem()})
        self.plot_item1.showGrid(x=True, y=True)
        self.plot_item1.setMouseEnabled(y=False)

        self.legend = self.plot_item1.addLegend((10, 10))

        self.plot_item2 = self.plot_view.ci.addPlot(row=1, col=0)
        # self.plot_item2.setAxisItems({"bottom": pg.DateAxisItem(utcOffset=0)})
        self.plot_item2.setAxisItems({"bottom": TimedeltaAxisItem()})
        self.plot_item2.showGrid(x=False, y=False)
        self.plot_item2.setMouseEnabled(x=False, y=False)

        self.region = pg.LinearRegionItem()
        # Add the LinearRegionItem to the ViewBox, but tell the ViewBox to exclude this
        # item when doing auto-range calculations.
        self.plot_item2.addItem(self.region, ignoreBounds=True)

        # TODO: check if needed
        # self.plot_item1.setAutoVisible(y=True)

        self.region.sigRegionChanged.connect(self._region_changed)
        self.plot_item1.sigXRangeChanged.connect(self._x_range_changed)

        self._layout.addWidget(self.plot_view)

        toolbar.addWidget(get_h_spacer_widget(toolbar))
        self.add_report_action = toolbar.addAction("Add Report")
        self.add_report_action.triggered.connect(self._add_report)

        self._refresh_data()

    def _destroyed(self):
        settings = QSettings()
        settings.setValue(
            self.__class__.__name__,
            FastLinePlotWidgetSettings(
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
        self.plot_item1.clear()
        self.plot_item2.clearPlots()
        self.legend.clear()

        grouping_settings = self.group_by_selector.get_grouping_settings()
        variable = self.variableSelector.get_selected_variable()

        columns = self.datatable.get_default_columns() + list(self.datatable.dataset.factors) + [variable.name]
        df = self.datatable.get_filtered_df(columns)

        df = group_by_columns(df, {variable.name: variable}, grouping_settings)

        match grouping_settings.mode:
            case GroupingMode.ANIMAL:
                if len(self.animals_table_view.selectedIndexes()) > 0:
                    df = df[df["Animal"].isin(self.animals_table_view.get_selected_animal_ids())]
                    df["Animal"] = df["Animal"].cat.remove_unused_categories()
                x_min, x_max = self._plot_animals(df, variable.name)
            case GroupingMode.FACTOR:
                factor = self.datatable.dataset.factors[grouping_settings.factor_name]
                x_min, x_max = self._plot_factors(df, variable.name, factor)
            case GroupingMode.RUN:
                x_min, x_max = self._plot_runs(df, variable.name)
            case _:
                x_min, x_max = self._plot_total(df, variable.name)

        # bound the LinearRegionItem to the plotted data
        self.region.setRegion([x_min, x_max])

    def _plot_item(self, data: pd.DataFrame, variable_name: str, name: str, pen):
        # x = (data["DateTime"] - pd.Timestamp("1970-01-01")) // pd.Timedelta("1s")  # Convert to POSIX timestamp
        x = data["Timedelta"].dt.total_seconds().to_numpy()
        y = data[variable_name].to_numpy()

        plot_data_item = (
            self.plot_item1.scatterPlot(x, y, pen=pen, size=2)
            if self.checkBoxScatterPlot.isChecked()
            else self.plot_item1.plot(x, y, pen=pen)
        )
        self.plot_item1.setTitle(variable_name)

        self.legend.addItem(plot_data_item, name)

        self.plot_item2.plot(x, y, pen=pen)

        if x.size != 0:
            return x.min(), x.max()
        else:
            return 0, 0

    def _plot_animals(self, df: pd.DataFrame, variable_name: str) -> tuple[float, float]:
        x_min = None
        x_max = None

        animal_ids = df["Animal"].cat.categories.tolist()

        for animal_id in animal_ids:
            animal = self.datatable.dataset.animals[animal_id]
            filtered_data = df[df["Animal"] == animal.id]

            pen = pg.mkPen(color=animal.color, width=1)
            tmp_min, tmp_max = self._plot_item(filtered_data, variable_name, animal.id, pen)

            if x_min is None or tmp_min < x_min:
                x_min = tmp_min
            if x_max is None or tmp_max > x_max:
                x_max = tmp_max

        return x_min, x_max

    def _plot_factors(self, df: pd.DataFrame, variable_name: str, factor: Factor) -> tuple[float, float]:
        x_min = None
        x_max = None

        for level in factor.levels:
            factor_data = df[df[factor.name] == level.name]

            pen = pg.mkPen(color=level.color, width=1)
            tmp_min, tmp_max = self._plot_item(factor_data, variable_name, f"{level.name}", pen)

            if x_min is None or tmp_min < x_min:
                x_min = tmp_min
            if x_max is None or tmp_max > x_max:
                x_max = tmp_max

        return x_min, x_max

    def _plot_runs(self, df: pd.DataFrame, variable_name: str) -> tuple[float, float]:
        x_min = None
        x_max = None

        runs = df["Run"].unique()
        for run in runs:
            run_data = df[df["Run"] == run]

            pen = pg.mkPen(color=color_manager.get_color_hex(int(run)), width=1)
            tmp_min, tmp_max = self._plot_item(run_data, variable_name, f"Run {run}", pen)

            if x_min is None or tmp_min < x_min:
                x_min = tmp_min
            if x_max is None or tmp_max > x_max:
                x_max = tmp_max

        return x_min, x_max

    def _plot_total(self, df: pd.DataFrame, variable_name: str) -> tuple[float, float]:
        pen = pg.mkPen(color=color_manager.get_color_hex(0), width=1)
        x_min, x_max = self._plot_item(df, variable_name, "Total", pen)
        return x_min, x_max

    def _region_changed(self):
        """Handle changes in the region selector.

        Updates the main plot's x-range when the region selector is moved.
        """
        min_x, max_x = self.region.getRegion()
        if not isnan(min_x) and not isnan(max_x):
            self.plot_item1.setXRange(min_x, max_x, padding=0)

    def _x_range_changed(self, view_box, range):
        """Handle changes in the main plot's x-range.

        Updates the region selector when the main plot's x-range is changed.

        Args:
            view_box: The view box that changed.
            range: The new x-range.
        """
        self.region.setRegion(range)

    def _add_report(self):
        exporter = ImageExporter(self.plot_item1)
        img = exporter.export(toBytes=True)

        ba = QByteArray()
        buffer = QBuffer(ba)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        img.save(buffer, "PNG")

        io = BytesIO(ba.data())
        encoded = base64.b64encode(io.getvalue()).decode("utf-8")
        html = f"<img src='data:image/png;base64,{encoded}'>"

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
