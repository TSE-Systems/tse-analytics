import numpy as np
import traja
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from matplotlib.pyplot import colorbar
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget
from traja import _get_after_plot_args, _label_axes, _process_after_plot_args

from tse_analytics.modules.phenomaster.actimot.views.actimot_heatmap_plot_widget_ui import Ui_ActimotHeatmapPlotWidget


class ActimotHeatmapPlotWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_ActimotHeatmapPlotWidget()
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
        normalize = self.ui.checkBoxNormalize.isChecked()
        log = self.ui.checkBoxLog.isChecked()

        after_plot_args, kwargs = _get_after_plot_args()

        bins = traja.trajectory._bins_to_tuple(self.trj_df, bins)
        # TODO: Add kde-based method for line-to-cell gridding
        df = self.trj_df[["x", "y"]].dropna()

        # Set aspect if `xlim` and `ylim` set.
        if "xlim" in kwargs and "ylim" in kwargs:
            xlim, ylim = kwargs.pop("xlim"), kwargs.pop("ylim")
        else:
            xlim, ylim = traja.trajectory._get_xylim(df)
        xmin, xmax = xlim
        ymin, ymax = ylim

        x, y = zip(*df.values)

        hist, x_edges, y_edges = np.histogram2d(
            x, y, bins, range=((xmin, xmax), (ymin, ymax)), density=normalize
        )

        # rotate to keep y as first dimension
        hist = np.rot90(hist)

        if log:
            hist = np.log(hist + np.e)

        image = ax.imshow(
            hist, interpolation="bilinear", aspect="equal", extent=[xmin, xmax, ymin, ymax], cmap="Reds"
        )
        # TODO: Adjust colorbar ytick_labels to correspond with time
        label = "Frames" if not log else "$ln(frames)$"
        colorbar(image, ax=ax, label=label)

        _label_axes(self.trj_df, ax)

        # plt.title("Time spent{}".format(" (Logarithmic)" if log else ""))

        _process_after_plot_args(**after_plot_args)

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()
