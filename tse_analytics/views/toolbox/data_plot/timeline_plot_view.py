import base64
from io import BytesIO

import pandas as pd
import pyqtgraph as pg
from PySide6.QtCore import QBuffer, QByteArray, QIODevice
from PySide6.QtWidgets import QWidget
from pyqtgraph.exporters import ImageExporter

from tse_analytics.core import color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Factor, SplitMode, Variable
from tse_analytics.views.misc.TimedeltaAxisItem import TimedeltaAxisItem


class TimelinePlotView(pg.GraphicsLayoutWidget):
    """Widget for displaying data as a timeline plot.

    This widget creates and displays timeline plots using PyQtGraph.
    It includes a main plot area and a smaller overview plot with a region selector
    that allows zooming into specific time ranges. It supports different grouping
    options, error bars, and scatter plot visualization.

    Attributes:
        plot_item1: The main plot area where data is displayed in detail.
        plot_item2: The overview plot area showing the entire timeline with a region selector.
        region: The linear region selector for zooming into specific time ranges.
        legend: The legend for the plot showing the color coding for different groups.
        datatable: The datatable containing the data being visualized.
        _df: The DataFrame containing the processed data for plotting.
        _variable: The variable being visualized.
        _split_mode: The mode for splitting/grouping the data.
        _selected_factor: The selected factor when split_mode is FACTOR.
        _error_type: The type of error bars to display ("std" or "sem").
        _display_errors: Whether to display error bars.
        _scatter_plot: Whether to display data as scatter points instead of lines.
    """

    def __init__(self, parent: QWidget):
        """Initialize the timeline plot view.

        Args:
            parent: The parent widget.
        """
        super().__init__(parent, show=False, size=None, title=None)

        # Set layout proportions
        self.ci.layout.setRowStretchFactor(0, 3)

        self.plot_item1 = self.ci.addPlot(row=0, col=0)
        # self.plot_item1.setAxisItems({"bottom": pg.DateAxisItem(utcOffset=0)})
        self.plot_item1.setAxisItems({"bottom": TimedeltaAxisItem()})
        self.plot_item1.showGrid(x=True, y=True)
        self.plot_item1.setMouseEnabled(y=False)

        self.legend = self.plot_item1.addLegend((10, 10))

        self.plot_item2 = self.ci.addPlot(row=1, col=0)
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

        # Local variables
        self.datatable: Datatable | None = None
        self._df: pd.DataFrame | None = None
        self._variable: Variable | None = None
        self._split_mode = SplitMode.ANIMAL
        self._selected_factor: Factor | None = None
        self._error_type = "std"
        self._display_errors = False
        self._scatter_plot = False

    def refresh_data(
        self,
        datatable: Datatable,
        df: pd.DataFrame,
        variable: Variable,
        split_mode: SplitMode,
        display_errors: bool,
        selected_factor: Factor | None,
        scatter_plot: bool,
    ) -> None:
        """Update the timeline plot with new data and settings.

        This method clears the existing plots and redraws them with the new data
        and settings. It handles different grouping options based on the split mode.

        Args:
            datatable: The datatable containing the data being visualized.
            df: The DataFrame containing the processed data for plotting.
            variable: The variable to visualize.
            split_mode: The mode for splitting/grouping the data.
            display_errors: Whether to display error bars.
            selected_factor: The selected factor when split_mode is FACTOR.
            scatter_plot: Whether to display data as scatter points instead of lines.
        """
        self.plot_item1.clear()
        self.plot_item2.clearPlots()
        self.legend.clear()

        if df.empty or (split_mode == SplitMode.FACTOR and selected_factor is None):
            self._df = None
            self._variable = None
            self._selected_factor = None
            self._display_errors = False
            return

        self.datatable = datatable
        self._df = df
        self._variable = variable
        self._split_mode = split_mode
        self._display_errors = display_errors
        self._selected_factor = selected_factor
        self._scatter_plot = scatter_plot

        match self._split_mode:
            case SplitMode.ANIMAL:
                x_min, x_max = self._plot_animals()
            case SplitMode.FACTOR:
                x_min, x_max = self._plot_factors()
            case SplitMode.RUN:
                x_min, x_max = self._plot_runs()
            case _:
                x_min, x_max = self._plot_total()

        # bound the LinearRegionItem to the plotted data
        self.region.setRegion([x_min, x_max])

    def _region_changed(self):
        """Handle changes in the region selector.

        Updates the main plot's x-range when the region selector is moved.
        """
        min_x, max_x = self.region.getRegion()
        self.plot_item1.setXRange(min_x, max_x, padding=0)

    def _x_range_changed(self, view_box, range):
        """Handle changes in the main plot's x-range.

        Updates the region selector when the main plot's x-range is changed.

        Args:
            view_box: The view box that changed.
            range: The new x-range.
        """
        self.region.setRegion(range)

    def _plot_item(self, data: pd.DataFrame, name: str, pen):
        """Plot a single data series on both the main and overview plots.

        This method plots the data for a single group (animal, factor level, run, or total)
        on both the main plot and the overview plot. It also adds error bars if enabled.

        Args:
            data: The DataFrame containing the data for this group.
            name: The name of the group to display in the legend.
            pen: The pen (color and style) to use for plotting.

        Returns:
            A tuple containing the minimum and maximum x values in the data.
        """
        # x = (data["DateTime"] - pd.Timestamp("1970-01-01")) // pd.Timedelta("1s")  # Convert to POSIX timestamp
        x = data["Timedelta"].dt.total_seconds().to_numpy()
        y = data[self._variable.name].to_numpy()

        plot_data_item = (
            self.plot_item1.scatterPlot(x, y, pen=pen, size=2)
            if self._scatter_plot
            else self.plot_item1.plot(x, y, pen=pen)
        )
        self.plot_item1.setTitle(self._variable.name)

        if self._display_errors and "Error" in data.columns:
            # Error bars
            error_plot = pg.ErrorBarItem(beam=0.2)
            error = data["Error"].to_numpy()
            error_plot.setData(x=x, y=y, top=error, bottom=error, pen=pen)
            self.plot_item1.addItem(error_plot)

            plot_data_item.visibleChanged.connect(lambda: error_plot.setVisible(plot_data_item.isVisible()))

        self.legend.addItem(plot_data_item, name)

        self.plot_item2.plot(x, y, pen=pen)

        if x.size != 0:
            return x.min(), x.max()
        else:
            return 0, 0

    def _plot_animals(self) -> tuple[float, float]:
        """Plot data grouped by animal.

        This method plots the data for each enabled animal in the dataset,
        with each animal represented by a different color.

        Returns:
            A tuple containing the minimum and maximum x values across all animals.
        """
        x_min = None
        x_max = None

        animals = [animal for animal in self.datatable.dataset.animals.values() if animal.enabled]

        for animal in animals:
            filtered_data = self._df[self._df["Animal"] == animal.id]

            pen = pg.mkPen(color=animal.color, width=1)
            tmp_min, tmp_max = self._plot_item(filtered_data, animal.id, pen)

            if x_min is None or tmp_min < x_min:
                x_min = tmp_min
            if x_max is None or tmp_max > x_max:
                x_max = tmp_max

        return x_min, x_max

    def _plot_factors(self) -> tuple[float, float]:
        """Plot data grouped by factor levels.

        This method plots the data for each level of the selected factor,
        with each level represented by a different color.

        Returns:
            A tuple containing the minimum and maximum x values across all factor levels.
        """
        x_min = None
        x_max = None

        factor_name = self._selected_factor.name

        levels = self._selected_factor.levels
        for level in levels:
            factor_data = self._df[self._df[factor_name] == level.name]

            pen = pg.mkPen(color=level.color, width=1)
            tmp_min, tmp_max = self._plot_item(factor_data, f"{level.name}", pen)

            if x_min is None or tmp_min < x_min:
                x_min = tmp_min
            if x_max is None or tmp_max > x_max:
                x_max = tmp_max

        return x_min, x_max

    def _plot_runs(self) -> tuple[float, float]:
        """Plot data grouped by run.

        This method plots the data for each run in the dataset,
        with each run represented by a different color.

        Returns:
            A tuple containing the minimum and maximum x values across all runs.
        """
        x_min = None
        x_max = None

        runs = self._df["Run"].unique()
        for run in runs:
            run_data = self._df[self._df["Run"] == run]

            pen = pg.mkPen(color=color_manager.get_color_hex(int(run)), width=1)
            tmp_min, tmp_max = self._plot_item(run_data, f"Run {run}", pen)

            if x_min is None or tmp_min < x_min:
                x_min = tmp_min
            if x_max is None or tmp_max > x_max:
                x_max = tmp_max

        return x_min, x_max

    def _plot_total(self) -> tuple[float, float]:
        """Plot data as a single total series.

        This method plots all the data as a single series without any grouping.

        Returns:
            A tuple containing the minimum and maximum x values in the data.
        """
        pen = pg.mkPen(color=color_manager.get_color_hex(0), width=1)
        x_min, x_max = self._plot_item(self._df, "Total", pen)
        return x_min, x_max

    def get_report(self) -> str:
        """Get an HTML representation of the current timeline plot for reporting.

        This method exports the main plot as a PNG image, encodes it as base64,
        and returns it as an HTML img tag that can be included in reports.

        Returns:
            HTML string containing the timeline plot image.
        """
        exporter = ImageExporter(self.plot_item1)
        img = exporter.export(toBytes=True)

        ba = QByteArray()
        buffer = QBuffer(ba)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        img.save(buffer, "PNG")

        io = BytesIO(ba.data())
        encoded = base64.b64encode(io.getvalue()).decode("utf-8")
        html = f"<img src='data:image/png;base64,{encoded}'>"
        return html
