import numpy as np
import traja
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget
from traja import _get_after_plot_args, _label_axes, _process_after_plot_args, coords_to_flow

from tse_analytics.modules.phenomaster.actimot.views.actimot_stream_plot_widget_ui import Ui_ActimotStreamPlotWidget


class ActimotStreamPlotWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_ActimotStreamPlotWidget()
        self.ui.setupUi(self)

        self.ui.toolButtonCalculate.clicked.connect(self.__update_plot)

        plot_toolbar = NavigationToolbar2QT(self.ui.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        self.ui.horizontalLayout.insertWidget(self.ui.horizontalLayout.count() - 1, plot_toolbar)

        self.trj_df: traja.TrajaDataFrame | None = None

    def set_data(self, trj_df: traja.TrajaDataFrame) -> None:
        self.trj_df = trj_df
        # self.__update_plot()

    def __update_plot(self):
        if self.trj_df is None:
            self.ui.canvas.clear(True)
            return

        self.ui.canvas.clear(False)
        ax = self.ui.canvas.figure.add_subplot(111)

        bins = self.ui.spinBoxBins.value()
        cmap = "Reds"

        after_plot_args, _ = _get_after_plot_args()
        X, Y, U, V = coords_to_flow(self.trj_df, bins)
        Z = np.sqrt(U * U + V * V)

        ax.contourf(X, Y, Z)
        ax.contour(X, Y, Z, colors="k", linewidths=1, linestyles="solid")
        ax.streamplot(X, Y, U, V, color=Z, cmap=cmap)

        ax = _label_axes(self.trj_df, ax)
        ax.set_aspect("equal")

        _process_after_plot_args(**after_plot_args)

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()
