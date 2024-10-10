import base64
from io import BytesIO

import numpy as np
import pandas as pd
import pyqtgraph as pg
from pyqtgraph import mkPen
from pyqtgraph.exporters import ImageExporter
from PySide6.QtCore import QBuffer, QByteArray, QIODevice
from PySide6.QtWidgets import QWidget

from tse_analytics.core.data.shared import Factor, SplitMode, Variable
from tse_analytics.core.manager import Manager
from tse_analytics.views.misc.TimedeltaAxisItem import TimedeltaAxisItem


class TimelinePlotView(pg.GraphicsLayoutWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent, show=False, size=None, title=None)

        # Set layout proportions
        self.ci.layout.setRowStretchFactor(0, 2)

        self.p1 = self.ci.addPlot(row=0, col=0)
        # self.p1.setAxisItems({"bottom": pg.DateAxisItem(utcOffset=0)})
        self.p1.setAxisItems({"bottom": TimedeltaAxisItem()})
        self.p1.showGrid(x=True, y=True)

        self.legend = self.p1.addLegend((10, 10))

        self.p2 = self.ci.addPlot(row=1, col=0)
        # self.p2.setAxisItems({"bottom": pg.DateAxisItem(utcOffset=0)})
        self.p2.setAxisItems({"bottom": TimedeltaAxisItem()})
        self.p2.showGrid(x=True, y=True)

        self.region = pg.LinearRegionItem()
        # Add the LinearRegionItem to the ViewBox, but tell the ViewBox to exclude this
        # item when doing auto-range calculations.
        self.p2.addItem(self.region, ignoreBounds=True)

        # self.p1.setAutoVisible(y=True)

        self.region.sigRegionChanged.connect(self.update)
        self.p1.sigRangeChanged.connect(self.updateRegion)

        # Local variables
        self._df: pd.DataFrame | None = None
        self._variable: Variable | None = None
        self._split_mode = SplitMode.ANIMAL
        self._selected_factor: Factor | None = None
        self._error_type = "std"
        self._display_errors = False
        self._scatter_plot = False

    def update(self):
        min_x, max_x = self.region.getRegion()
        self.p1.setXRange(min_x, max_x, padding=0)

    def updateRegion(self, window, viewRange):
        rgn = viewRange[0]
        self.region.setRegion(rgn)

    def set_data(self, df: pd.DataFrame) -> None:
        self._df = df

        if self._df.empty:
            self.p1.clear()
            self.p2.clearPlots()
            self.legend.clear()
            return

        unique_deltas = self._df["Timedelta"].unique()
        TimedeltaAxisItem.sampling_interval = unique_deltas[1] - unique_deltas[0]

        self._update_plot()

    def set_variable(self, variable: Variable, update: bool):
        self._variable = variable
        if update:
            self._update_plot()

    def set_split_mode(self, grouping_mode: SplitMode, selected_factor: Factor):
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
        self.p1.clear()
        self.p2.clearPlots()
        self.legend.clear()

        if (
            self._df is None
            or self._variable is None
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
            case _:
                x_min, x_max = self._plot_total()

        # bound the LinearRegionItem to the plotted data
        self.region.setClipItem(self.p2)
        self.region.setRegion([x_min, x_max])

        self.update()

    def _plot_item(self, data: pd.DataFrame, name: str, pen):
        # x = (data["DateTime"] - pd.Timestamp("1970-01-01")) // pd.Timedelta("1s")  # Convert to POSIX timestamp
        x = data["Bin"]

        x = x.to_numpy(dtype=np.int64)
        tmp_min = x.min()
        tmp_max = x.max()

        # y = data[self._variable].to_numpy()
        y = data[self._variable.name].to_numpy()

        # p1d = self.p1.plot(x, y, symbol='o', symbolSize=2, symbolPen=pen, pen=pen)
        p1d = self.p1.scatterPlot(x, y, pen=pen, size=2) if self._scatter_plot else self.p1.plot(x, y, pen=pen)
        self.p1.setTitle(self._variable.name)

        if self._display_errors and self._split_mode != SplitMode.ANIMAL:
            # Error bars
            error_plot = pg.ErrorBarItem(beam=0.2)
            error = data["Error"].to_numpy()
            error_plot.setData(x=x, y=y, top=error, bottom=error, pen=pen)
            self.p1.addItem(error_plot)

            p1d.visibleChanged.connect(lambda: error_plot.setVisible(p1d.isVisible()))

        self.legend.addItem(p1d, name)

        self.p2.plot(x, y, pen=pen)

        return tmp_min, tmp_max

    def _plot_animals(self) -> tuple[float, float]:
        x_min = None
        x_max = None

        animals = [animal for animal in Manager.data.selected_dataset.animals.values() if animal.enabled]

        for i, animal in enumerate(animals):
            filtered_data = self._df[self._df["Animal"] == animal.id]

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

        # group_by = ["Bin", factor_name]
        # grouped = self._df.groupby(group_by, dropna=False, observed=False)
        #
        # result = (
        #     grouped.agg(
        #         Value=(self._variable.name, self._variable.aggregation),
        #         Error=(self._variable.name, self._error_type),
        #     )
        #     if self._display_errors
        #     else grouped.agg(
        #         Value=(self._variable.name, self._variable.aggregation),
        #     )
        # )
        #
        # data = result.reset_index()
        # data.rename(columns={"Value": self._variable.name}, inplace=True)

        data = self._df

        groups = self._selected_factor.groups
        for i, group in enumerate(groups):
            filtered_data = data[data[factor_name] == group.name]

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

        # group_by = ["Bin", "Run"]
        # grouped = self._df.groupby(group_by, dropna=False, observed=False)
        #
        # result = (
        #     grouped.agg(
        #         Value=(self._variable.name, self._variable.aggregation),
        #         Error=(self._variable.name, np.std),
        #     )
        #     if self._display_errors
        #     else grouped.agg(
        #         Value=(self._variable.name, self._variable.aggregation),
        #     )
        # )
        #
        # data = result.reset_index()
        # data.rename(columns={"Value": self._variable.name}, inplace=True)

        data = self._df

        runs = data["Run"].unique()
        for i, run in enumerate(runs):
            filtered_data = data[data["Run"] == run]

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

        # group_by = ["Bin"]
        # grouped = self._df.groupby(group_by, dropna=False, observed=False)
        #
        # result = (
        #     grouped.agg(
        #         Value=(self._variable.name, self._variable.aggregation),
        #         Error=(self._variable.name, self._error_type),
        #     )
        #     if self._display_errors
        #     else grouped.agg(
        #         Value=(self._variable.name, self._variable.aggregation),
        #     )
        # )
        #
        # data = result.reset_index()
        # data.rename(columns={"Value": self._variable.name}, inplace=True)

        data = self._df

        pen = mkPen(color=(1, 1), width=1)
        tmp_min, tmp_max = self._plot_item(data, "Total", pen)

        if x_min is None or tmp_min < x_min:
            x_min = tmp_min
        if x_max is None or tmp_max > x_max:
            x_max = tmp_max

        return x_min, x_max

    def clear_plot(self):
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
