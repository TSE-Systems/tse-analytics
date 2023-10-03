from typing import Optional, Union

import pandas as pd
import pyqtgraph as pg
from PySide6.QtWidgets import QWidget
from pyqtgraph import mkPen

from tse_analytics.core.manager import Manager
from tse_datatools.analysis.grouping_mode import GroupingMode


class TimelinePlotView(pg.GraphicsLayoutWidget):
    def __init__(self, parent: QWidget, title="Plot"):
        super().__init__(parent, title=title)

        self._df: Optional[pd.DataFrame] = None
        self._variable: str = ""
        self._display_errors = False

        # Set layout proportions
        self.ci.layout.setRowStretchFactor(0, 2)

        self.label = self.addLabel(row=0, col=0, justify="right")

        self.plot_data_items: dict[Union[int, str], pg.PlotDataItem] = {}

        self.p1: pg.PlotItem = self.addPlot(row=0, col=0)
        # customize the averaged curve that can be activated from the context menu:
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

        # Crosshair
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.p1.addItem(self.vLine, ignoreBounds=True)
        self.p1.addItem(self.hLine, ignoreBounds=True)

        self.view_box = self.p1.vb

        # self.proxy = pg.SignalProxy(self.p1.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)

    def update(self):
        self.region.setZValue(10)
        minX, maxX = self.region.getRegion()
        self.p1.setXRange(minX, maxX, padding=0)

    def updateRegion(self, window, viewRange):
        rgn = viewRange[0]
        self.region.setRegion(rgn)

    # def mouseMoved(self, evt):
    #     pos = evt[0]  # using signal proxy turns original arguments into a tuple
    #     if self.start_datetime is not None and self.p1.sceneBoundingRect().contains(pos):
    #         mousePoint = self.view_box.mapSceneToView(pos)
    #         dt = datetime.fromtimestamp(mousePoint.x())
    #         index = (dt - self.start_datetime) // self.timedelta  # Convert to POSIX timestamp
    #         index = int(index)
    #         keys = list(self.plot_data_items.keys())
    #         if len(keys) > 0 and (0 < index < len(self.plot_data_items[keys[0]].yData)):
    #             spans = ""
    #             for animal in self._animals:
    #                 spans = spans + f",  <span>Animal {animal.id}={self.plot_data_items[animal.id].yData[index]}</span>"
    #             text = f'<span style="font-size: 8pt">x={datetime.fromtimestamp(self.plot_data_items[animal.id].xData[index])}{spans}</span>'
    #             self.label.setText(text)
    #             self.vLine.setPos(mousePoint.x())
    #             self.hLine.setPos(mousePoint.y())

    def set_data(self, df: pd.DataFrame):
        self._df = df
        self.__update_plot()

    def set_variable(self, variable: str, update: bool):
        self._variable = variable
        if update:
            self.__update_plot()

    def set_display_errors(self, state: bool):
        self._display_errors = state
        self.__update_plot()

    def __update_plot(self):
        self.plot_data_items.clear()
        self.p1.clear()
        self.p2.clearPlots()
        self.legend.clear()

        if (
            self._df is None
            or self._variable == ""
            or (Manager.data.grouping_mode == GroupingMode.FACTORS and Manager.data.selected_factor is None)
        ):
            return

        if Manager.data.grouping_mode == GroupingMode.ANIMALS:
            animals = (
                Manager.data.selected_animals
                if len(Manager.data.selected_animals) > 0
                else Manager.data.selected_dataset.animals.values()
            )
            for i, animal in enumerate(animals):
                filtered_data = self._df[self._df["Animal"] == animal.id]

                x = (filtered_data["DateTime"] - pd.Timestamp("1970-01-01")) // pd.Timedelta(
                    "1s"
                )  # Convert to POSIX timestamp
                x = x.to_numpy()
                # x = filtered_data["Bin"].to_numpy()
                y = filtered_data[self._variable].to_numpy()

                pen = mkPen(color=(i, len(animals)), width=1)
                # p1d = self.p1.plot(x, y, symbol='o', symbolSize=2, symbolPen=pen, pen=pen)
                p1d = self.p1.plot(x, y, pen=pen)

                if self._display_errors:
                    # Error bars
                    error_plot = pg.ErrorBarItem(beam=0.2)
                    std = filtered_data["Std"]
                    std = std.to_numpy()
                    error_plot.setData(x=x, y=y, top=std, bottom=std)
                    self.p1.addItem(error_plot)

                self.plot_data_items[animal.id] = p1d
                self.legend.addItem(p1d, f"Animal {animal.id}")

                p2d: pg.PlotDataItem = self.p2.plot(x, y, pen=pen)
        elif Manager.data.grouping_mode == GroupingMode.FACTORS:
            groups = Manager.data.selected_factor.groups
            for i, group in enumerate(groups):
                factor_name = Manager.data.selected_factor.name
                filtered_data = self._df[self._df[factor_name] == group.name]

                x = (filtered_data["DateTime"] - pd.Timestamp("1970-01-01")) // pd.Timedelta(
                    "1s"
                )  # Convert to POSIX timestamp
                x = x.to_numpy()
                # x = filtered_data["Bin"].to_numpy()
                y = filtered_data[self._variable].to_numpy()

                # pen = (i, len(Manager.data.selected_groups))
                pen = mkPen(color=(i, len(groups)), width=1)
                # p1d = self.p1.plot(x, y, symbol='o', symbolSize=2, symbolPen=pen, pen=pen)
                p1d = self.p1.plot(x, y, pen=pen)

                if self._display_errors:
                    # Error bars
                    error_plot = pg.ErrorBarItem(beam=0.2)
                    std = filtered_data["Std"]
                    std = std.to_numpy()
                    error_plot.setData(x=x, y=y, top=std, bottom=std)
                    self.p1.addItem(error_plot)

                self.plot_data_items[group.name] = p1d
                self.legend.addItem(p1d, f"{group.name}")

                p2d: pg.PlotDataItem = self.p2.plot(x, y, pen=pen)
        elif Manager.data.grouping_mode == GroupingMode.RUNS:
            runs = self._df["Run"].unique()
            for i, run in enumerate(runs):
                filtered_data = self._df[self._df["Run"] == run]

                x = (filtered_data["DateTime"] - pd.Timestamp("1970-01-01")) // pd.Timedelta(
                    "1s"
                )  # Convert to POSIX timestamp
                x = x.to_numpy()
                # x = filtered_data["Bin"].to_numpy()
                y = filtered_data[self._variable].to_numpy()

                pen = mkPen(color=(i, len(runs)), width=1)
                # p1d = self.p1.plot(x, y, symbol='o', symbolSize=2, symbolPen=pen, pen=pen)
                p1d = self.p1.plot(x, y, pen=pen)

                self.plot_data_items[run] = p1d
                self.legend.addItem(p1d, f"Run {run}")

                p2d: pg.PlotDataItem = self.p2.plot(x, y, pen=pen)

        # bound the LinearRegionItem to the plotted data
        self.region.setClipItem(p2d)
        if len(x) > 0:
            self.region.setRegion([x.min(), x.max()])

        self.update()

    def clear_plot(self):
        self.plot_data_items.clear()
        self.p1.clear()
        self.p2.clearPlots()
        self.legend.clear()

        self._df = None
        self._variable = None
        self._display_errors = False
