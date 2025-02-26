import datetime

import pandas as pd
import pyqtgraph as pg
from pyqtgraph import mkPen
from PySide6.QtWidgets import QWidget


class MealDetailsPlotView(pg.GraphicsLayoutWidget):
    def __init__(self, parent: QWidget, title="MealDetailsPlot"):
        super().__init__(parent, title=title)

        self._df: pd.DataFrame | None = None
        self._variable: str = ""

        self._start_datetime = None
        self._timedelta = None

        # Set layout proportions
        self.ci.layout.setRowStretchFactor(0, 2)

        self.label = self.addLabel(row=0, col=0, justify="right")

        self.plot_data_items: dict[int | str, pg.PlotDataItem] = {}

        self.p1: pg.PlotItem = self.addPlot(row=0, col=0)
        # customize the averaged curve that can be activated from the context menu:
        self.p1.avgPen = pg.mkPen("#FFFFFF")
        self.p1.avgShadowPen = pg.mkPen("#8080DD", width=10)
        self.p1.setAxisItems({"bottom": pg.DateAxisItem()})
        self.p1.showGrid(x=True, y=True)

        self.legend = self.p1.addLegend((10, 10))

        self.p2: pg.PlotItem = self.addPlot(row=1, col=0)
        self.p2.setAxisItems({"bottom": pg.DateAxisItem()})
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
        minX, maxX = self.region.getRegion()
        self.p1.setXRange(minX, maxX, padding=0)

    def updateRegion(self, window, viewRange):
        rgn = viewRange[0]
        self.region.setRegion(rgn)

    def set_data(self, df: pd.DataFrame):
        self._df = df
        self._update_plot()

    def set_variable(self, variable: str):
        self._variable = variable
        self._update_plot()

    def _update_plot(self):
        self.plot_data_items.clear()
        self.p1.clear()
        self.p2.clearPlots()
        self.legend.clear()

        if self._df is None or self._variable == "":
            return

        box_ids = self._df["Box"].unique().tolist()
        for i, box_id in enumerate(box_ids):
            filtered_data = self._df[self._df["Box"] == box_id]

            x = filtered_data["DateTime"]
            x = (x - pd.Timestamp("1970-01-01")) // pd.Timedelta("1s")  # Convert to POSIX timestamp
            x = x.to_numpy()
            y = filtered_data[self._variable].to_numpy()

            pen = mkPen(color=(i, len(box_ids)), width=1)
            # p1d = self.p1.plot(x, y, symbol='o', symbolSize=2, symbolPen=pen, pen=pen)
            p1d = self.p1.plot(x, y, pen=pen)

            self.plot_data_items[box_id] = p1d
            self.legend.addItem(p1d, f"Box {box_id}")

            p2d: pg.PlotDataItem = self.p2.plot(x, y, pen=pen)

        # bound the LinearRegionItem to the plotted data
        self.region.setClipItem(p2d)
        if len(x) > 0:
            self.region.setRegion([x.min(), x.max()])
            self._start_datetime = datetime.datetime.fromtimestamp(x[0])
            self._timedelta = pd.Timedelta(
                datetime.datetime.fromtimestamp(x[1]) - datetime.datetime.fromtimestamp(x[0])
            )

        self.update()

    def clear_plot(self):
        self.plot_data_items.clear()
        self.p1.clear()
        self.p2.clearPlots()
        self.legend.clear()

        self._df = None
        self._variable = None
        self._start_datetime = None
        self._timedelta = None
