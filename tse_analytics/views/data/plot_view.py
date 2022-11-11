from typing import Optional, Union
import datetime

import pandas as pd
import pyqtgraph as pg

from PySide6.QtWidgets import QWidget

from tse_analytics.core.view_mode import ViewMode
from tse_analytics.messaging.messages import BinningAppliedMessage
from tse_datatools.analysis.processor import apply_time_binning
from tse_datatools.data.animal import Animal
from tse_datatools.data.group import Group


class PlotView(pg.GraphicsLayoutWidget):
    def __init__(self, parent: QWidget, title="Plot"):
        super().__init__(parent, title=title)

        self._df: Optional[pd.DataFrame] = None
        self._animals: Optional[list[Animal]] = None
        self._groups: Optional[list[Group]] = None
        self._variable: str = ''
        self._view_mode: ViewMode = ViewMode.ANIMALS

        # Set layout proportions
        self.ci.layout.setRowStretchFactor(0, 2)

        self.label = self.addLabel(row=0, col=0, justify='right')

        self.plot_data_items: dict[Union[int, str], pg.PlotDataItem] = {}

        self.p1: pg.PlotItem = self.addPlot(row=0, col=0)
        # customize the averaged curve that can be activated from the context menu:
        self.p1.avgPen = pg.mkPen('#FFFFFF')
        self.p1.avgShadowPen = pg.mkPen('#8080DD', width=10)
        self.p1.setAxisItems({'bottom': pg.DateAxisItem()})
        self.p1.showGrid(x=True, y=True)

        self.legend = self.p1.addLegend((10, 10))

        self.p2: pg.PlotItem = self.addPlot(row=1, col=0)
        self.p2.setAxisItems({'bottom': pg.DateAxisItem()})
        self.p2.showGrid(x=True, y=True)

        self.region = pg.LinearRegionItem()
        self.region.setZValue(10)
        # Add the LinearRegionItem to the ViewBox, but tell the ViewBox to exclude this
        # item when doing auto-range calculations.
        self.p2.addItem(self.region, ignoreBounds=True)

        self.p1.setAutoVisible(y=True)

        self.start_datetime = None
        self.timedelta = None

        self.region.sigRegionChanged.connect(self.update)

        self.p1.sigRangeChanged.connect(self.updateRegion)

        # self.region.setRegion([1000, 2000])

        # Crosshair
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.p1.addItem(self.vLine, ignoreBounds=True)
        self.p1.addItem(self.hLine, ignoreBounds=True)

        self.view_box = self.p1.vb

        self.proxy = pg.SignalProxy(self.p1.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)

    def update(self):
        self.region.setZValue(10)
        minX, maxX = self.region.getRegion()
        self.p1.setXRange(minX, maxX, padding=0)

    def updateRegion(self, window, viewRange):
        rgn = viewRange[0]
        self.region.setRegion(rgn)

    def mouseMoved(self, evt):
        pos = evt[0]  # using signal proxy turns original arguments into a tuple
        if self.start_datetime is not None and self.p1.sceneBoundingRect().contains(pos):
            mousePoint = self.view_box.mapSceneToView(pos)
            dt = datetime.datetime.fromtimestamp(mousePoint.x())
            index = (dt - self.start_datetime) // self.timedelta  # Convert to POSIX timestamp
            index = int(index)
            keys = list(self.plot_data_items.keys())
            if len(keys) > 0 and (0 < index < len(self.plot_data_items[keys[0]].yData)):
                spans = ""
                for animal in self._animals:
                    spans = spans + f',  <span>Animal {animal.id}={self.plot_data_items[animal.id].yData[index]}</span>'
                text = f'<span style="font-size: 8pt">x={datetime.datetime.fromtimestamp(self.plot_data_items[animal.id].xData[index])}{spans}</span>'
                self.label.setText(text)
                self.vLine.setPos(mousePoint.x())
                self.hLine.setPos(mousePoint.y())

    def set_data(self, df: pd.DataFrame):
        self._df = df
        self.__update_plot()

    def filter_animals(self, animals: list[Animal]):
        self._view_mode = ViewMode.ANIMALS
        self._animals = animals
        self.__update_plot()

    def filter_groups(self, groups: list[Group]):
        self._view_mode = ViewMode.GROUPS
        self._groups = groups
        self.__update_plot()

    def set_variable(self, variable: str):
        self._variable = variable
        self.__update_plot()

    def apply_binning(self, message: BinningAppliedMessage):
        self._df = apply_time_binning(self._df, message.delta, message.unit, message.mode)
        self.__update_plot()

    def __update_plot(self):
        self.plot_data_items.clear()
        self.p1.clearPlots()
        self.p2.clearPlots()
        self.legend.clear()

        if self._df is None or self._variable == '':
            return

        if self._view_mode == ViewMode.ANIMALS:
            if self._animals is None or len(self._animals) == 0:
                return
        elif self._view_mode == ViewMode.GROUPS:
            if self._groups is None or len(self._groups) == 0:
                return

        if self._view_mode == ViewMode.ANIMALS:
            for i, animal in enumerate(self._animals):
                filtered_data = self._df[self._df['Animal'] == animal.id]

                x = filtered_data["DateTime"]
                x = (x - pd.Timestamp("1970-01-01")) // pd.Timedelta("1s")  # Convert to POSIX timestamp
                x = x.to_numpy()
                y = filtered_data[self._variable].to_numpy()
                pen = (i, len(self._animals))

                p1d = self.p1.plot(x, y, pen=pen)
                self.plot_data_items[animal.id] = p1d
                self.legend.addItem(p1d, f'Animal {animal.id}')

                p2d: pg.PlotDataItem = self.p2.plot(x, y, pen=pen)
        elif self._view_mode == ViewMode.GROUPS:
            for i, group in enumerate(self._groups):
                filtered_data = self._df[self._df['Group'] == group.name]

                x = filtered_data["DateTime"]
                x = (x - pd.Timestamp("1970-01-01")) // pd.Timedelta("1s")  # Convert to POSIX timestamp
                x = x.to_numpy()
                y = filtered_data[self._variable].to_numpy()
                pen = (i, len(self._groups))

                p1d = self.p1.plot(x, y, pen=pen)
                self.plot_data_items[group.name] = p1d
                self.legend.addItem(p1d, f'Group {group.name}')

                p2d: pg.PlotDataItem = self.p2.plot(x, y, pen=pen)

        # bound the LinearRegionItem to the plotted data
        self.region.setClipItem(p2d)
        self.region.setRegion([x.min(), x.max()])

        self.start_datetime = datetime.datetime.fromtimestamp(x[0])
        self.timedelta = pd.Timedelta(datetime.datetime.fromtimestamp(x[1]) - datetime.datetime.fromtimestamp(x[0]))
        self.update()

    def clear_plot(self):
        self.plot_data_items.clear()
        self.p1.clearPlots()
        self.p2.clearPlots()
        self.legend.clear()

        self._df = None
        self._animals = None
        self._variable = None
        self.start_datetime = None
        self.timedelta = None
