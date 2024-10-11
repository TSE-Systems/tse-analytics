import traja
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget

from tse_analytics.core.helper import make_toast
from tse_analytics.core.manager import Manager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.modules.phenomaster.actimot.views.actimot_trajectory_plot_widget_ui import (
    Ui_ActimotTrajectoryPlotWidget,
)


class ActimotTrajectoryPlotWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_ActimotTrajectoryPlotWidget()
        self.ui.setupUi(self)

        self.ui.toolButtonCalculate.clicked.connect(self._update_plot)
        self.ui.checkBoxDrawNPoints.toggled.connect(lambda toggled: self.ui.spinBoxN.setEnabled(toggled))

        plot_toolbar = NavigationToolbar2QT(self.ui.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        self.ui.horizontalLayout.insertWidget(self.ui.horizontalLayout.count() - 1, plot_toolbar)

        self.trj_df: traja.TrajaDataFrame | None = None

        self.toast = None

    def set_data(self, trj_df: traja.TrajaDataFrame) -> None:
        self.trj_df = trj_df
        # self.update_plot()

    def _update_plot(self):
        if self.trj_df is None:
            self.ui.canvas.clear(True)
            return

        self.ui.toolButtonCalculate.setEnabled(False)

        self.toast = make_toast(self, "ActiMot Trajectory Analysis", "Processing...")
        self.toast.show()

        worker = Worker(self._work)
        worker.signals.finished.connect(self._work_finished)
        Manager.threadpool.start(worker)

    def _work(self):
        self.ui.canvas.clear(False)
        ax = self.ui.canvas.figure.add_subplot(111)

        n_points = None
        if self.ui.checkBoxDrawNPoints.isChecked():
            n_points = self.ui.spinBoxN.value()

        _ = traja.plot(self.trj_df, ax=ax, n_coords=n_points)

    def _work_finished(self):
        self.toast.hide()
        self.ui.toolButtonCalculate.setEnabled(True)

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()
