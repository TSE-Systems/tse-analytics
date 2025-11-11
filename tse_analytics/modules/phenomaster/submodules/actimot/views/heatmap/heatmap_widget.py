import traja
import seaborn as sns
import numpy as np
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget

from tse_analytics.core.toaster import make_toast
from tse_analytics.core.workers.task_manager import TaskManager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.modules.phenomaster.submodules.actimot.views.heatmap.heatmap_widget_ui import Ui_HeatmapWidget


class HeatmapWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_HeatmapWidget()
        self.ui.setupUi(self)

        self.ui.toolButtonCalculate.clicked.connect(self._update_plot)

        plot_toolbar = NavigationToolbar2QT(self.ui.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        self.ui.horizontalLayout.insertWidget(self.ui.horizontalLayout.count() - 1, plot_toolbar)

        self.trj_df: traja.TrajaDataFrame | None = None
        self.toast = None

    def set_data(self, trj_df: traja.TrajaDataFrame | None) -> None:
        self.trj_df = trj_df
        self.ui.toolButtonCalculate.setEnabled(trj_df is not None)

    def _update_plot(self):
        if self.trj_df is None:
            self.ui.canvas.clear(True)
            return

        self.ui.canvas.clear(False)
        self.ui.toolButtonCalculate.setEnabled(False)

        self.toast = make_toast(self, "ActiMot Heatmap", "Processing...")
        self.toast.show()

        worker = Worker(self._work)
        worker.signals.result.connect(self._work_result)
        TaskManager.start_task(worker)

    def _work(self):
        bins = self.ui.spinBoxBins.value()
        normalize = self.ui.checkBoxNormalize.isChecked()
        log = self.ui.checkBoxLog.isChecked()

        hist, _ = traja.trip_grid(
            self.trj_df,
            bins=bins,
            log=log,
            normalize=normalize,
            hist_only=True,
        )

        return hist

    def _work_result(self, hist: np.ndarray):
        self.toast.hide()
        self.ui.toolButtonCalculate.setEnabled(True)

        ax = self.ui.canvas.figure.add_subplot(1, 1, 1)

        sns.heatmap(hist, ax=ax,)

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()
