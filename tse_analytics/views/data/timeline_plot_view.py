import pandas as pd
import pyqtgraph as pg
from pyqtgraph import mkPen
from PySide6.QtWidgets import QWidget

from tse_analytics.core.data.shared import Factor, GroupingMode
from tse_analytics.core.manager import Manager


class TimelinePlotView(pg.GraphicsLayoutWidget):
    def __init__(self, parent: QWidget, title="Plot"):
        super().__init__(parent, title=title)

        self._df: pd.DataFrame | None = None
        self._variable = ""
        self._grouping_mode = GroupingMode.ANIMALS
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
        self.p1.setAxisItems({"bottom": pg.DateAxisItem(utcOffset=0)})
        self.p1.showGrid(x=True, y=True)

        self.legend = self.p1.addLegend((10, 10))

        self.p2: pg.PlotItem = self.addPlot(row=1, col=0)
        self.p2.setAxisItems({"bottom": pg.DateAxisItem(utcOffset=0)})
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

    def set_data(self, df: pd.DataFrame):
        self._df = df
        self.__update_plot()

    def set_variable(self, variable: str, update: bool):
        self._variable = variable
        if update:
            self.__update_plot()

    def set_grouping_mode(self, grouping_mode: GroupingMode, selected_factor: Factor):
        self._grouping_mode = grouping_mode
        self._selected_factor = selected_factor

    def set_display_errors(self, state: bool):
        self._display_errors = state
        self.__update_plot()

    def set_error_type(self, error_type: str):
        self._error_type = error_type
        self.__update_plot()

    def set_scatter_plot(self, state: bool):
        self._scatter_plot = state
        self.__update_plot()

    def __update_plot(self):
        self.plot_data_items.clear()
        self.p1.clear()
        self.p2.clearPlots()
        self.legend.clear()

        if (
            self._df is None
            or self._variable == ""
            or (self._grouping_mode == GroupingMode.FACTORS and self._selected_factor is None)
        ):
            return

        match self._grouping_mode:
            case GroupingMode.ANIMALS:
                x_min, x_max = self.__plot_animals()
            case GroupingMode.FACTORS:
                x_min, x_max = self.__plot_factors()
            case GroupingMode.RUNS:
                x_min, x_max = self.__plot_runs()

        # bound the LinearRegionItem to the plotted data
        self.region.setClipItem(self.p2)
        self.region.setRegion([x_min, x_max])

        self.update()

    def __plot_item(self, data: pd.DataFrame, name: str, pen):
        x = (data["DateTime"] - pd.Timestamp("1970-01-01")) // pd.Timedelta("1s")  # Convert to POSIX timestamp
        # x = filtered_data["Bin"]

        x = x.to_numpy()
        tmp_min = x.min()
        tmp_max = x.max()

        # y = data[self._variable].to_numpy()
        y = data[self._variable].to_numpy()

        # p1d = self.p1.plot(x, y, symbol='o', symbolSize=2, symbolPen=pen, pen=pen)
        p1d = self.p1.scatterPlot(x, y, pen=pen, size=2) if self._scatter_plot else self.p1.plot(x, y, pen=pen)

        if self._display_errors and self._grouping_mode != GroupingMode.ANIMALS:
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

    def __plot_animals(self) -> tuple[float, float]:
        x_min = None
        x_max = None

        animals = (
            Manager.data.selected_animals
            if len(Manager.data.selected_animals) > 0
            else Manager.data.selected_dataset.animals.values()
        )

        for i, animal in enumerate(animals):
            filtered_data = self._df[self._df["Animal"] == animal.id]

            pen = mkPen(color=(i, len(animals)), width=1)
            tmp_min, tmp_max = self.__plot_item(filtered_data, f"Animal {animal.id}", pen)

            if x_min is None or tmp_min < x_min:
                x_min = tmp_min
            if x_max is None or tmp_max > x_max:
                x_max = tmp_max

        return x_min, x_max

    def __plot_factors(self) -> tuple[float, float]:
        x_min = None
        x_max = None

        factor_name = self._selected_factor.name

        group_by = ["DateTime", factor_name]
        grouped = self._df.groupby(group_by, dropna=False, observed=False)

        result = (
            grouped.agg(
                Value=(self._variable, Manager.data.binning_params.operation.value),
                Error=(self._variable, self._error_type),
            )
            if self._display_errors
            else grouped.agg(
                Value=(self._variable, Manager.data.binning_params.operation.value),
            )
        )

        data = result.reset_index()
        data.rename(columns={"Value": self._variable}, inplace=True)

        groups = self._selected_factor.groups
        for i, group in enumerate(groups):
            filtered_data = data[data[factor_name] == group.name]

            pen = mkPen(color=(i, len(groups)), width=1)
            tmp_min, tmp_max = self.__plot_item(filtered_data, f"{group.name}", pen)

            if x_min is None or tmp_min < x_min:
                x_min = tmp_min
            if x_max is None or tmp_max > x_max:
                x_max = tmp_max

        return x_min, x_max

    def __plot_runs(self) -> tuple[float, float]:
        x_min = None
        x_max = None

        group_by = ["DateTime", "Run"]
        grouped = self._df.groupby(group_by, dropna=False, observed=False)

        result = (
            grouped.agg(
                Value=(self._variable, Manager.data.binning_params.operation.value),
                Error=(self._variable, self._error_type),
            )
            if self._display_errors
            else grouped.agg(
                Value=(self._variable, Manager.data.binning_params.operation.value),
            )
        )

        data = result.reset_index()
        data.rename(columns={"Value": self._variable}, inplace=True)

        runs = self._df["Run"].unique()
        for i, run in enumerate(runs):
            filtered_data = data[data["Run"] == run]

            pen = mkPen(color=(i, len(runs)), width=1)
            tmp_min, tmp_max = self.__plot_item(filtered_data, f"Run {run}", pen)

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
