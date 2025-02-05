import pandas as pd
import pyqtgraph as pg
from PySide6.QtWidgets import QWidget

from tse_analytics.modules.phenomaster.trafficage.data.trafficage_data import TraffiCageData


class TraffiCageActivityWidget(pg.GraphicsLayoutWidget):
    def __init__(self, parent: QWidget | None = None):
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

        self.region.sigRegionChanged.connect(self._region_changed)
        self.p1.sigXRangeChanged.connect(self._x_range_changed)

    def _region_changed(self):
        min_x, max_x = self.region.getRegion()
        self.p1.setXRange(min_x, max_x, padding=0)

    def _x_range_changed(self, view_box, range):
        self.region.setRegion(range)

    def set_data(self, data: TraffiCageData):
        if data.df is None:
            return

        x_min, x_max = self._plot_animals(data)
        # bound the LinearRegionItem to the plotted data
        self.region.setRegion([x_min, x_max])

    def _plot_animals(self, data: TraffiCageData) -> tuple[float, float]:
        x_min = None
        x_max = None

        for i, animal in enumerate(data.dataset.animals.values()):
            filtered_data = data.df[data.df["Animal"] == animal.id]
            if filtered_data.empty:
                continue

            pen = pg.mkPen(color=(i, len(data.dataset.animals)), width=1)
            tmp_min, tmp_max = self._plot_item(filtered_data, animal.id, pen)

            if x_min is None or tmp_min < x_min:
                x_min = tmp_min
            if x_max is None or tmp_max > x_max:
                x_max = tmp_max

        return x_min, x_max

    def _plot_item(self, df: pd.DataFrame, name: str, pen):
        x = df["DateTime"]
        x = (x - pd.Timestamp("1970-01-01")) // pd.Timedelta("1s")  # Convert to POSIX timestamp
        x = x.to_numpy()
        y = df["Activity"].to_numpy()

        plot_data_item = self.p1.plot(x, y, pen=pen)
        self.p1.setTitle("Activity")
        self.legend.addItem(plot_data_item, name)

        self.p2.plot(x, y, pen=pen)

        return x.min(), x.max()
