import base64
from io import BytesIO

import polars as pl
import pyqtgraph as pg
from pyqtgraph import mkPen
from pyqtgraph.exporters import ImageExporter
from PySide6.QtCore import QBuffer, QByteArray, QIODevice
from PySide6.QtWidgets import QWidget

from tse_analytics.core.data.binning import BinningOperation
from tse_analytics.core.data.shared import Factor, SplitMode
from tse_analytics.core.manager import Manager
from tse_analytics.views.misc.TimedeltaAxisItem import TimedeltaAxisItem


class TimelinePlotView(pg.GraphicsLayoutWidget):
    def __init__(self, parent: QWidget, title="Plot"):
        super().__init__(parent, title=title)

        self._df: pl.DataFrame | None = None
        self._variable = ""
        self._split_mode = SplitMode.ANIMAL
        self._selected_factor: Factor | None = None
        self._error_type = "std"
        self._display_errors = False
        self._scatter_plot = False

        # Set layout proportions
        self.ci.layout.setRowStretchFactor(0, 2)

        self.label = self.addLabel(row=0, col=0, justify="right")

        self.plot_data_items: dict[int | str, pg.PlotDataItem] = {}

        self.p1: pg.PlotItem = self.addPlot(row=0, col=0)
        # customize the averaged curve that can be activated from the context menu
        self.p1.avgPen = pg.mkPen("#FFFFFF")
        self.p1.avgShadowPen = pg.mkPen("#8080DD", width=10)
        # self.p1.setAxisItems({"bottom": pg.DateAxisItem(utcOffset=0)})
        self.p1.setAxisItems({"bottom": TimedeltaAxisItem()})
        self.p1.showGrid(x=True, y=True)

        self.legend = self.p1.addLegend((10, 10))

        self.p2: pg.PlotItem = self.addPlot(row=1, col=0)
        # self.p2.setAxisItems({"bottom": pg.DateAxisItem(utcOffset=0)})
        self.p2.setAxisItems({"bottom": TimedeltaAxisItem()})
        self.p2.showGrid(x=True, y=True)

        self.region = pg.LinearRegionItem()
        self.region.setZValue(10)
        # Add the LinearRegionItem to the ViewBox, but tell the ViewBox to exclude this
        # item when doing auto-range calculations.
        self.p2.addItem(self.region, ignoreBounds=True)

        self.p1.setAutoVisible(y=True)

        self.region.sigRegionChanged.connect(self.update)

        self.p1.sigRangeChanged.connect(self.updateRegion)

    def update(self):
        self.region.setZValue(10)
        min_x, max_x = self.region.getRegion()
        self.p1.setXRange(min_x, max_x, padding=0)

    def updateRegion(self, window, viewRange):
        rgn = viewRange[0]
        self.region.setRegion(rgn)

    def set_data(self, df: pl.DataFrame):
        self._df = df

        unique_deltas = self._df["Timedelta"].unique()
        TimedeltaAxisItem.sampling_interval = unique_deltas[1] - unique_deltas[0]

        self._update_plot()

    def set_variable(self, variable: str, update: bool):
        self._variable = variable
        if update:
            self._update_plot()

    def set_grouping_mode(self, grouping_mode: SplitMode, selected_factor: Factor):
        self._split_mode = grouping_mode
        self._selected_factor = selected_factor

    def set_display_errors(self, state: bool):
        self._display_errors = state
        self._update_plot()

    def set_error_type(self, error_type: str):
        self._error_type = error_type
        self._update_plot()

    def set_scatter_plot(self, state: bool):
        self._scatter_plot = state
        self._update_plot()

    def _update_plot(self):
        self.plot_data_items.clear()
        self.p1.clear()
        self.p2.clearPlots()
        self.legend.clear()

        if (
            self._df is None
            or self._variable == ""
            or (self._split_mode == SplitMode.FACTOR and self._selected_factor is None)
        ):
            return

        match self._split_mode:
            case SplitMode.ANIMAL:
                x_min, x_max = self._plot_animals()
            case SplitMode.FACTOR:
                x_min, x_max = self._plot_factors()
            case SplitMode.RUN:
                x_min, x_max = self._plot_runs()
            case SplitMode.TOTAL:
                x_min, x_max = self._plot_total()

        # bound the LinearRegionItem to the plotted data
        self.region.setClipItem(self.p2)
        self.region.setRegion([x_min, x_max])

        self.update()

    def _plot_item(self, data: pl.DataFrame, name: str, pen):
        x = data["Bin"].to_numpy()

        tmp_min = x.min()
        tmp_max = x.max()

        y = data[self._variable].to_numpy()

        # p1d = self.p1.plot(x, y, symbol='o', symbolSize=2, symbolPen=pen, pen=pen)
        p1d = self.p1.scatterPlot(x, y, pen=pen, size=2) if self._scatter_plot else self.p1.plot(x, y, pen=pen)
        self.p1.setTitle(self._variable)

        if self._display_errors and self._split_mode != SplitMode.ANIMAL:
            # Error bars
            error_plot = pg.ErrorBarItem(beam=0.2)
            error = data["Error"].to_numpy()
            error_plot.setData(x=x, y=y, top=error, bottom=error, pen=pen)
            self.p1.addItem(error_plot)

            p1d.visibleChanged.connect(lambda: error_plot.setVisible(p1d.isVisible()))

        self.plot_data_items[name] = p1d
        self.legend.addItem(p1d, name)

        self.p2.plot(x, y, pen=pen)

        return tmp_min, tmp_max

    def _plot_animals(self) -> tuple[float, float]:
        x_min = None
        x_max = None

        animals = (
            Manager.data.selected_animals
            if len(Manager.data.selected_animals) > 0
            else Manager.data.selected_dataset.animals.values()
        )

        for i, animal in enumerate(animals):
            filtered_data = self._df.filter(pl.col("Animal") == animal.id)

            pen = mkPen(color=(i, len(animals)), width=1)
            tmp_min, tmp_max = self._plot_item(filtered_data, f"Animal {animal.id}", pen)

            if x_min is None or tmp_min < x_min:
                x_min = tmp_min
            if x_max is None or tmp_max > x_max:
                x_max = tmp_max

        return x_min, x_max

    def _plot_factors(self) -> tuple[float, float]:
        x_min = None
        x_max = None

        factor_name = self._selected_factor.name

        match Manager.data.binning_params.operation:
            case BinningOperation.MEAN:
                expr = pl.mean(self._variable)
            case BinningOperation.MEDIAN:
                expr = pl.median(self._variable)
            case _:
                expr = pl.sum(self._variable)

        if self._display_errors:
            data = self._df.group_by(["Bin", factor_name], maintain_order=True).agg(
                expr,
                Error=pl.std(self._variable))
        else:
            data = self._df.group_by(["Bin", factor_name], maintain_order=True).agg(expr)

        groups = self._selected_factor.groups
        for i, group in enumerate(groups):
            filtered_data = data.filter(pl.col(factor_name) == group.name)

            pen = mkPen(color=(i, len(groups)), width=1)
            tmp_min, tmp_max = self._plot_item(filtered_data, f"{group.name}", pen)

            if x_min is None or tmp_min < x_min:
                x_min = tmp_min
            if x_max is None or tmp_max > x_max:
                x_max = tmp_max

        return x_min, x_max

    def _plot_runs(self) -> tuple[float, float]:
        x_min = None
        x_max = None

        match Manager.data.binning_params.operation:
            case BinningOperation.MEAN:
                expr = pl.mean(self._variable)
            case BinningOperation.MEDIAN:
                expr = pl.median(self._variable)
            case _:
                expr = pl.sum(self._variable)

        if self._display_errors:
            data = self._df.group_by(["Bin", "Run"], maintain_order=True).agg(
                expr,
                Error=pl.std(self._variable))
        else:
            data = self._df.group_by(["Bin", "Run"], maintain_order=True).agg(expr)

        # result = (
        #     grouped.agg(
        #         Value=(self._variable, Manager.data.binning_params.operation.value),
        #         Error=(self._variable, self._error_type),
        #     )
        #     if self._display_errors
        #     else grouped.agg(
        #         Value=(self._variable, Manager.data.binning_params.operation.value),
        #     )
        # )

        runs = self._df["Run"].unique()
        for i, run in enumerate(runs):
            filtered_data = data.filter(pl.col("Run") == run)

            pen = mkPen(color=(i, len(runs)), width=1)
            tmp_min, tmp_max = self._plot_item(filtered_data, f"Run {run}", pen)

            if x_min is None or tmp_min < x_min:
                x_min = tmp_min
            if x_max is None or tmp_max > x_max:
                x_max = tmp_max

        return x_min, x_max

    def _plot_total(self) -> tuple[float, float]:
        x_min = None
        x_max = None

        match Manager.data.binning_params.operation:
            case BinningOperation.MEAN:
                expr = pl.mean(self._variable)
            case BinningOperation.MEDIAN:
                expr = pl.median(self._variable)
            case _:
                expr = pl.sum(self._variable)

        if self._display_errors:
            data = self._df.group_by(["Bin"], maintain_order=True).agg(
                expr,
                Error=pl.std(self._variable))
        else:
            data = self._df.group_by(["Bin"], maintain_order=True).agg(expr)

        pen = mkPen(color=(1, 1), width=1)
        tmp_min, tmp_max = self._plot_item(data, "Total", pen)

        if x_min is None or tmp_min < x_min:
            x_min = tmp_min
        if x_max is None or tmp_max > x_max:
            x_max = tmp_max

        return x_min, x_max

    def clear_plot(self):
        self.plot_data_items.clear()
        self.p1.clear()
        self.p2.clearPlots()
        self.legend.clear()

        self._df = None
        self._variable = None
        self._display_errors = False

    def get_report(self) -> str:
        exporter = ImageExporter(self.p1)
        img = exporter.export(toBytes=True)

        ba = QByteArray()
        buffer = QBuffer(ba)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        img.save(buffer, "PNG")

        io = BytesIO(ba.data())
        encoded = base64.b64encode(io.getvalue()).decode("utf-8")
        html = f"<img src='data:image/png;base64,{encoded}'>"
        return html
