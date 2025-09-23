import pandas as pd
import pyqtgraph as pg
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QWidget, QToolBar, QVBoxLayout, QCheckBox

from tse_analytics.modules.phenomaster.submodules.grouphousing.data.grouphousing_data import GroupHousingData


class ActivityWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        # Setup toolbar
        toolbar = QToolBar(
            "Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        self.data = None
        self.preprocessed_data: dict[str, pd.DataFrame] | None = None
        self._include_drinkfeed = False

        self.checkBoxIncludeDrinkFeed = QCheckBox("Include DrinkFeed", toolbar)
        self.checkBoxIncludeDrinkFeed.checkStateChanged.connect(self._include_drinkfeed_changed)
        toolbar.addWidget(self.checkBoxIncludeDrinkFeed)

        # Insert the toolbar to the widget
        self._layout.addWidget(toolbar)

        self._glw = pg.GraphicsLayoutWidget(self, show=False, size=None, title=None)
        self._layout.addWidget(self._glw)

        # Set layout proportions
        self._glw.ci.layout.setRowStretchFactor(0, 2)

        self.p1 = self._glw.ci.addPlot(row=0, col=0)
        self.p1.setAxisItems({"bottom": pg.DateAxisItem()})
        self.p1.showGrid(x=True, y=True)

        self.legend = self.p1.addLegend((10, 10))

        self.p2 = self._glw.ci.addPlot(row=1, col=0)
        self.p2.setAxisItems({"bottom": pg.DateAxisItem()})
        self.p2.showGrid(x=True, y=True)

        self.region = pg.LinearRegionItem()
        # Add the LinearRegionItem to the ViewBox, but tell the ViewBox to exclude this
        # item when doing auto-range calculations.
        self.p2.addItem(self.region, ignoreBounds=True)

        # self.p1.setAutoVisible(y=True)

        self.region.sigRegionChanged.connect(self._region_changed)
        self.p1.sigXRangeChanged.connect(self._x_range_changed)

    def set_preprocessed_data(self, data: GroupHousingData, preprocessed_data: dict[str, pd.DataFrame]):
        self.data = data
        self.preprocessed_data = preprocessed_data
        self._refresh_plot()

    def _include_drinkfeed_changed(self, state: Qt.CheckState) -> None:
        self._include_drinkfeed = state == Qt.CheckState.Checked
        self._refresh_plot()

    def _refresh_plot(self):
        self.p1.clear()
        self.p2.clearPlots()
        self.legend.clear()

        df = self.preprocessed_data["All"] if self._include_drinkfeed else self.preprocessed_data["TraffiCage"]
        x_min, x_max = self._plot_animals(self.data, df)
        # bound the LinearRegionItem to the plotted data
        self.region.setRegion([x_min, x_max])

    def _region_changed(self):
        min_x, max_x = self.region.getRegion()
        self.p1.setXRange(min_x, max_x, padding=0)

    def _x_range_changed(self, view_box, range):
        self.region.setRegion(range)

    def _plot_animals(self, data: GroupHousingData, df: pd.DataFrame) -> tuple[float, float]:
        x_min = None
        x_max = None

        for i, animal in enumerate(data.dataset.animals.values()):
            filtered_data = df[df["Animal"] == animal.id]
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
