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
    def __init__(self, parent: QWidget):
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
        min_x, max_x = self.region.getRegion()
        self.plot_item1.setXRange(min_x, max_x, padding=0)

    def _x_range_changed(self, view_box, range):
        self.region.setRegion(range)

    def _plot_item(self, data: pd.DataFrame, name: str, pen):
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
        pen = pg.mkPen(color=color_manager.get_color_hex(0), width=1)
        x_min, x_max = self._plot_item(self._df, "Total", pen)
        return x_min, x_max

    def get_report(self) -> str:
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
