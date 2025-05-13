from matplotlib.backends.backend_qt import NavigationToolbar2QT
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget, QToolBar

from tse_analytics.core import messaging
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.utils import get_h_spacer_widget, get_html_image
from tse_analytics.views.misc.MplCanvas import MplCanvas


class PlotWidget(QWidget):
    def __init__(self, datatable: Datatable, parent=None):
        super().__init__(parent)

        self.datatable = datatable

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.canvas = MplCanvas(self)

        # Setup toolbar
        toolbar = QToolBar(
            "Plot Widget Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        plot_toolbar = NavigationToolbar2QT(self.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        toolbar.addWidget(plot_toolbar)

        toolbar.addWidget(get_h_spacer_widget(toolbar))
        toolbar.addAction("Add to Report").triggered.connect(self._add_report)

        self.layout.addWidget(toolbar)
        self.layout.addWidget(self.canvas)

    def clear(self, redraw: bool):
        self.canvas.clear(redraw)

    def _add_report(self):
        self.datatable.dataset.report += get_html_image(self.canvas.figure)
        messaging.broadcast(messaging.AddToReportMessage(self, self.datatable.dataset))
