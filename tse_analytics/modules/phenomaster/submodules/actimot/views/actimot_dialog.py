import timeit

import pandas as pd
import traja
from pyqttoast import ToastPreset
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QIcon, QKeyEvent, QHideEvent
from PySide6.QtWidgets import QDialog, QFileDialog, QWidget

from tse_analytics.core.data.shared import Aggregation, Variable
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.workers.task_manager import TaskManager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.modules.phenomaster.submodules.actimot.actimot_processor import calculate_trj
from tse_analytics.modules.phenomaster.submodules.actimot.actimot_settings import ActimotSettings
from tse_analytics.modules.phenomaster.submodules.actimot.data.actimot_animal_item import ActimotAnimalItem
from tse_analytics.modules.phenomaster.submodules.actimot.data.actimot_data import ActimotData
from tse_analytics.modules.phenomaster.submodules.actimot.views.actimot_box_selector import ActimotBoxSelector
from tse_analytics.modules.phenomaster.submodules.actimot.views.actimot_dialog_ui import Ui_ActimotDialog
from tse_analytics.modules.phenomaster.submodules.actimot.views.actimot_frames_widget import ActimotFramesWidget
from tse_analytics.modules.phenomaster.submodules.actimot.views.actimot_heatmap_plot_widget import (
    ActimotHeatmapPlotWidget,
)
from tse_analytics.modules.phenomaster.submodules.actimot.views.actimot_plot_widget import ActimotPlotWidget
from tse_analytics.modules.phenomaster.submodules.actimot.views.actimot_settings_widget import ActimotSettingsWidget
from tse_analytics.modules.phenomaster.submodules.actimot.views.actimot_stream_plot_widget import (
    ActimotStreamPlotWidget,
)
from tse_analytics.modules.phenomaster.submodules.actimot.views.actimot_table_view import ActimotTableView
from tse_analytics.modules.phenomaster.submodules.actimot.views.actimot_trajectory_plot_widget import (
    ActimotTrajectoryPlotWidget,
)


class ActimotDialog(QDialog):
    def __init__(self, actimot_data: ActimotData, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_ActimotDialog()
        self.ui.setupUi(self)

        settings = QSettings()
        self.restoreGeometry(settings.value("ActimotDialog/Geometry"))

        self.actimot_data = actimot_data

        self.actimot_table_view = ActimotTableView(self)
        self.ui.tabWidget.addTab(self.actimot_table_view, "Events")

        self.actimot_plot_widget = ActimotPlotWidget(self)
        self.ui.tabWidget.addTab(self.actimot_plot_widget, "Events Plot")

        self.actimot_frames_widget = ActimotFramesWidget(self)
        self.ui.tabWidget.addTab(self.actimot_frames_widget, "Frames")

        self.actimot_trajectory_plot_widget = ActimotTrajectoryPlotWidget(self)
        self.ui.tabWidget.addTab(self.actimot_trajectory_plot_widget, "Trajectory")

        self.actimot_stream_plot_widget = ActimotStreamPlotWidget(self)
        self.ui.tabWidget.addTab(self.actimot_stream_plot_widget, "Stream")

        self.actimot_heatmap_plot_widget = ActimotHeatmapPlotWidget(self)
        self.ui.tabWidget.addTab(self.actimot_heatmap_plot_widget, "Heatmap")

        self.ui.toolButtonPreprocess.clicked.connect(self._preprocess)
        self.ui.toolButtonExport.clicked.connect(self._export_data)

        self.actimot_settings_widget = ActimotSettingsWidget(self)
        try:
            actimot_settings = settings.value("ActimotSettings", ActimotSettings.get_default())
            self.actimot_settings_widget.set_data(self.actimot_data.dataset, actimot_settings)
        except Exception:
            actimot_settings = ActimotSettings.get_default()
            self.actimot_settings_widget.set_data(self.actimot_data.dataset, actimot_settings)

        self.actimot_box_selector = ActimotBoxSelector(self._select_box, self.actimot_settings_widget, self)
        self.actimot_box_selector.set_data(actimot_data.dataset)

        self.ui.toolBox.removeItem(0)
        self.ui.toolBox.addItem(self.actimot_box_selector, QIcon(":/icons/icons8-dog-tag-16.png"), "Boxes")
        self.ui.toolBox.addItem(self.actimot_settings_widget, QIcon(":/icons/icons8-dog-tag-16.png"), "Settings")

        self.df: pd.DataFrame | None = None

    def _select_box(self, selected_box: ActimotAnimalItem) -> None:
        self.ui.toolButtonExport.setEnabled(False)

        self.df = self.actimot_data.raw_df[self.actimot_data.raw_df["Box"] == selected_box.box]

        self.actimot_table_view.set_data(self.df)
        self.actimot_frames_widget.set_data(self.df)

        self.actimot_trajectory_plot_widget.set_data(None)
        self.actimot_stream_plot_widget.set_data(None)
        self.actimot_heatmap_plot_widget.set_data(None)

    def _preprocess(self) -> None:
        if self.df is None:
            make_toast(
                self,
                "ActiMot Preprocessing",
                "Please select a single box.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        actimot_settings = self.actimot_settings_widget.get_settings()
        if (
            actimot_settings.use_smooting
            and actimot_settings.smoothing_window_size is not None
            and actimot_settings.smoothing_window_size % 2 != 1
        ):
            make_toast(
                self,
                "ActiMot Preprocessing",
                "Smoothing window size must be odd.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        tic = timeit.default_timer()

        toast = make_toast(self, "ActiMot Preprocessing", "Please wait...")
        toast.show()

        def _work_result(result: tuple[pd.DataFrame, traja.TrajaDataFrame]) -> None:
            toast.hide()

            df, trj_df = result

            # Add custom variables
            self.actimot_data.variables["x"] = Variable(
                "x",
                "cm",
                "Centroid X",
                "float64",
                Aggregation.MEAN,
                False,
            )

            self.actimot_data.variables["y"] = Variable(
                "y",
                "cm",
                "Centroid Y",
                "float64",
                Aggregation.MEAN,
                False,
            )

            self.actimot_data.variables["displacement"] = Variable(
                "displacement",
                "cm",
                "Displacement",
                "float64",
                Aggregation.MEAN,
                False,
            )

            self.actimot_data.variables["speed"] = Variable(
                "speed",
                "cm/s",
                "Speed",
                "float64",
                Aggregation.MEAN,
                False,
            )

            self.actimot_data.variables["acceleration"] = Variable(
                "acceleration",
                "cm/s²",
                "Acceleration",
                "float64",
                Aggregation.MEAN,
                False,
            )

            self.actimot_table_view.set_data(df)

            self.actimot_plot_widget.set_variables(self.actimot_data.variables)
            self.actimot_plot_widget.set_data(df)

            self.actimot_trajectory_plot_widget.set_data(trj_df)
            self.actimot_stream_plot_widget.set_data(trj_df)
            self.actimot_heatmap_plot_widget.set_data(trj_df)

            self.df = df

            self.ui.toolButtonExport.setEnabled(True)

            make_toast(
                self,
                "ActiMot Preprocessing",
                f"ActiMot preprocessing complete in {(timeit.default_timer() - tic):.3f} sec.",
                duration=4000,
                preset=ToastPreset.SUCCESS,
                show_duration_bar=True,
                echo_to_logger=True,
            ).show()

        def _work_finished() -> None:
            pass

        worker = Worker(calculate_trj, self.df, actimot_settings)
        worker.signals.result.connect(_work_result)
        worker.signals.finished.connect(_work_finished)
        TaskManager.start_task(worker)

    def _export_data(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export to CSV", "ActiMotEvents", "CSV Files (*.csv)")
        if filename:
            self.df.to_csv(filename, sep=";", index=False)

    def hideEvent(self, event: QHideEvent) -> None:
        settings = QSettings()
        settings.setValue("ActimotDialog/Geometry", self.saveGeometry())

        actimot_settings = self.actimot_settings_widget.get_settings()
        settings.setValue("ActimotSettings", actimot_settings)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Escape:
            return
        super().keyPressEvent(event)
