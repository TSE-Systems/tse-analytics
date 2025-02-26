import pandas as pd
import pyqtgraph as pg
from PySide6.QtWidgets import QWidget


class ActimotPlotView(pg.GraphicsLayoutWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent, show=False, size=None, title=None)

        # Set layout proportions
        self.ci.layout.setRowStretchFactor(0, 2)

        self.p1 = self.ci.addPlot(row=0, col=0)
        self.p1.setAxisItems({"bottom": pg.DateAxisItem()})
        self.p1.showGrid(x=True, y=True)

        self.legend = self.p1.addLegend((10, 10))

        self.p2 = self.ci.addPlot(row=1, col=0)
        self.p2.setAxisItems({"bottom": pg.DateAxisItem()})
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
        self._variable: str = ""

    def update(self):
        min_x, max_x = self.region.getRegion()
        self.p1.setXRange(min_x, max_x, padding=0)

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
        self.p1.clear()
        self.p2.clearPlots()
        self.legend.clear()

        if self._df is None or self._variable == "":
            return

        x = self._df["DateTime"]
        x = (x - pd.Timestamp("1970-01-01")) // pd.Timedelta("1s")  # Convert to POSIX timestamp
        x = x.to_numpy()
        y = self._df[self._variable].to_numpy()

        pen = pg.mkPen(color=(1, 1), width=1)
        p1d = self.p1.plot(x, y, pen=pen)
        self.p1.setTitle(self._variable)

        self.legend.addItem(p1d, self._variable)

        p2d = self.p2.plot(x, y, pen=pen)

        # bound the LinearRegionItem to the plotted data
        self.region.setClipItem(p2d)
        self.region.setRegion([x.min(), x.max()])

        self.update()

    def clear_plot(self):
        self.p1.clear()
        self.p2.clearPlots()
        self.legend.clear()

        self._df = None
        self._variable = None
