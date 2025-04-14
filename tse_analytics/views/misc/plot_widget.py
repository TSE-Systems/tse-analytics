from matplotlib.backends.backend_qt import NavigationToolbar2QT
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QVBoxLayout, QWidget

from tse_analytics.views.misc.MplCanvas import MplCanvas


class PlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.canvas = MplCanvas(self)

        plot_toolbar = NavigationToolbar2QT(self.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))

        self.layout.addWidget(plot_toolbar)
        self.layout.addWidget(self.canvas)
