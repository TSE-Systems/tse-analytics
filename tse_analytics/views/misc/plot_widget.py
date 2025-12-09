from matplotlib.backends.backend_qt import NavigationToolbar2QT
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QInputDialog, QToolBar, QVBoxLayout, QWidget

from tse_analytics.core import manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.report import Report
from tse_analytics.core.utils import get_h_spacer_widget, get_html_image_from_figure
from tse_analytics.views.misc.MplCanvas import MplCanvas


class PlotWidget(QWidget):
    """
    A widget for displaying matplotlib plots with navigation controls.

    This widget provides a canvas for matplotlib figures along with a toolbar
    that includes standard plot navigation controls (zoom, pan, save, etc.)
    and the ability to add the plot to a report.
    """

    def __init__(self, datatable: Datatable, parent=None):
        """
        Initialize the PlotWidget.

        Args:
            datatable: The Datatable object associated with this widget.
            parent: The parent widget. Default is None.
        """
        super().__init__(parent)

        self.datatable = datatable

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Plot"

        self.canvas = MplCanvas(self)

        # Setup toolbar
        toolbar = QToolBar(
            "Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        plot_toolbar = NavigationToolbar2QT(self.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        toolbar.addWidget(plot_toolbar)

        toolbar.addWidget(get_h_spacer_widget(toolbar))
        toolbar.addAction("Add Report").triggered.connect(self._add_report)

        self._layout.addWidget(toolbar)
        self._layout.addWidget(self.canvas)

    def clear(self, redraw: bool):
        """
        Clear the plot canvas.

        This method removes all plots, axes, and other elements from the canvas.

        Args:
            redraw: If True, the canvas will be redrawn after clearing.
                   If False, the canvas will not be redrawn until explicitly requested.
        """
        self.canvas.clear(redraw)

    def _add_report(self):
        name, ok = QInputDialog.getText(
            self,
            "Report",
            "Please enter report name:",
            text=self.title,
        )
        if ok and name:
            manager.add_report(
                Report(
                    self.datatable.dataset,
                    name,
                    get_html_image_from_figure(self.canvas.figure),
                )
            )
