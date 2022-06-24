import weakref

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGraphicsGridLayout
from pyqtgraph import GraphicsWidget, ViewBox, LinearRegionItem, AxisItem, PlotCurveItem, \
    Point


class HistogramItem(GraphicsWidget):
    """
    This is a graphicsWidget which provides controls for adjusting the display of an image.

    Includes:

    - Image histogram
    - Movable region over histogram to select black/white levels

    Parameters
    ----------
    image : ImageItem or None
        If *image* is provided, then the control will be automatically linked to
        the image and changes to the control will be immediately reflected in
        the image's appearance.
    fillHistogram : bool
        By default, the histogram is rendered with a fill.
        For performance, set *fillHistogram* = False.
    """

    sigLevelsChanged = Signal(object)
    sigLevelChangeFinished = Signal(object)

    def __init__(self, image=None, fillHistogram=True, bounds: tuple = None):
        super().__init__()
        self.imageItem = lambda: None  # fake a dead weakref

        self.layout = QGraphicsGridLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(1, 1, 1, 1)
        self.layout.setSpacing(0)
        self.vb = ViewBox(parent=self)
        # self.vb.setMaximumHeight(152)
        # self.vb.setMinimumWidth(45)
        self.vb.setMouseEnabled(x=True, y=False)

        self.region = LinearRegionItem([0, 1], 'vertical', swapMode='block', bounds=bounds)
        self.region.setZValue(1000)
        self.vb.addItem(self.region)
        self.region.lines[0].addMarker('<|', 0.5)
        self.region.lines[1].addMarker('|>', 0.5)
        self.region.sigRegionChanged.connect(self.regionChanging)
        self.region.sigRegionChangeFinished.connect(self.regionChanged)

        self.axis = AxisItem('bottom', linkView=self.vb, maxTickLength=-10, parent=self)
        self.layout.addItem(self.axis, 1, 0)
        self.layout.addItem(self.vb, 0, 0)
        self.range = None
        self.vb.sigRangeChanged.connect(self.viewRangeChanged)

        self.plot = PlotCurveItem(pen=(200, 200, 200, 100))
        # self.plot.rotate(90)
        self.vb.addItem(self.plot)

        self.fillHistogram(fillHistogram)
        self._showRegions()

        self.autoHistogramRange()

        if image is not None:
            self.setImageItem(image)

    def fillHistogram(self, fill=True, level=0.0, color=(100, 100, 200)):
        if fill:
            self.plot.setFillLevel(level)
            self.plot.setBrush(color)
        else:
            self.plot.setFillLevel(None)


    def paint(self, p, *args):
        rgn = self.getLevels()
        self.vb.mapFromViewToItem(self, Point(self.vb.viewRect().center().x(), rgn[0]))
        self.vb.mapFromViewToItem(self, Point(self.vb.viewRect().center().x(), rgn[1]))


    def setHistogramRange(self, mn, mx, padding=0.1):
        """Set the Y range on the histogram plot. This disables auto-scaling."""
        self.vb.enableAutoRange(self.vb.XAxis, False)
        self.vb.setYRange(mn, mx, padding)

    def autoHistogramRange(self):
        """Enable auto-scaling on the histogram plot."""
        self.vb.enableAutoRange(self.vb.XYAxes)

    def setImageItem(self, img):
        """Set an ImageItem to have its levels and LUT automatically controlled
        by this HistogramLUTItem.
        """
        self.imageItem = weakref.ref(img)
        img.sigImageChanged.connect(self.imageChanged)
        self.regionChanged()
        self.imageChanged(autoLevel=True)

    def viewRangeChanged(self):
        self.update()

    def regionChanged(self):
        if self.imageItem() is not None:
            self.imageItem().setLevels(self.getLevels())
        self.sigLevelChangeFinished.emit(self)

    def regionChanging(self):
        if self.imageItem() is not None:
            self.imageItem().setLevels(self.getLevels())
        self.sigLevelsChanged.emit(self)
        self.update()

    def imageChanged(self, autoLevel=False):
        if self.imageItem() is None:
            return

        self.plot.setVisible(True)
        # plot one histogram for all image data
        h = self.imageItem().getHistogram()
        if h[0] is None:
            return
        self.plot.setData(*h)
        if autoLevel:
            mn = h[0][0]
            mx = h[0][-1]
            self.region.setRegion([mn, mx])
        else:
            mn, mx = self.imageItem().levels
            self.region.setRegion([mn, mx])

    def getLevels(self):
        """
        Return the min and max levels.
        """
        return self.region.getRegion()

    def setLevels(self, min=None, max=None):
        """
        Set the min/max (bright and dark) levels.
        """
        assert None not in (min, max)
        self.region.setRegion((min, max))

    def _showRegions(self):
        self.region.setVisible(True)

    def saveState(self):
        return {
            'levels': self.getLevels(),
        }

    def restoreState(self, state):
        self.setLevels(*state['levels'])
