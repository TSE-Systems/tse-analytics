import pandas as pd
import traja
from pyqttoast import ToastPreset
from PySide6.QtCore import QSettings, QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QToolBar, QWidget

from tse_analytics.core.data.shared import Aggregation, Variable
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.workers.task_manager import TaskManager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.modules.phenomaster.submodules.actimot.actimot_settings import ActimotSettings
from tse_analytics.modules.phenomaster.submodules.actimot.data.actimot_animal_item import ActimotAnimalItem
from tse_analytics.modules.phenomaster.submodules.actimot.data.actimot_data import ActimotData
from tse_analytics.modules.phenomaster.submodules.actimot.processor import calculate_trj
from tse_analytics.modules.phenomaster.submodules.actimot.views.actimot_widget_ui import Ui_ActimotWidget
from tse_analytics.modules.phenomaster.submodules.actimot.views.box_selector import BoxSelector
from tse_analytics.modules.phenomaster.submodules.actimot.views.frames.frames_widget import FramesWidget
from tse_analytics.modules.phenomaster.submodules.actimot.views.heatmap.heatmap_widget import HeatmapWidget
from tse_analytics.modules.phenomaster.submodules.actimot.views.plot.plot_widget import PlotWidget
from tse_analytics.modules.phenomaster.submodules.actimot.views.settings.settings_widget import SettingsWidget
from tse_analytics.modules.phenomaster.submodules.actimot.views.stream.stream_widget import (
    StreamWidget,
)
from tse_analytics.modules.phenomaster.submodules.actimot.views.trajectory.trajectory_widget import TrajectoryWidget
from tse_analytics.views.misc.pandas_widget import PandasWidget


class ActimotWidget(QWidget):
    def __init__(self, actimot_data: ActimotData, parent: QWidget):
        super().__init__(parent)

        self.ui = Ui_ActimotWidget()
        self.ui.setupUi(self)

        self.setWindowFlags(
            Qt.WindowType.Window
            # | Qt.WindowType.CustomizeWindowHint
            # | Qt.WindowType.WindowTitleHint
            # | Qt.WindowType.WindowCloseButtonHint
        )

        # Connect destructor to save settings
        self.destroyed.connect(lambda: self._destroyed())

        settings = QSettings()

        self.actimot_data = actimot_data
        self.df: pd.DataFrame | None = None
        self.trj_df: traja.TrajaDataFrame | None = None
        self.toast = None

        # Setup toolbar
        toolbar = QToolBar(
            "Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        self.preprocess_action = toolbar.addAction(QIcon(":/icons/icons8-analyze-16.png"), "Preprocess")
        self.preprocess_action.triggered.connect(self._preprocess)

        self.ui.verticalLayout.insertWidget(0, toolbar)

        self.table_view = PandasWidget(actimot_data.dataset, "ActiMot Events")
        self.ui.tabWidget.addTab(self.table_view, "Events")

        self.frames_widget = FramesWidget(self)
        self.ui.tabWidget.addTab(self.frames_widget, "Frames")

        self.plot_widget = PlotWidget(self)
        self.plot_tab_index = self.ui.tabWidget.addTab(self.plot_widget, "Events Plot")

        self.trajectory_widget = TrajectoryWidget(self)
        self.trajectory_tab_index = self.ui.tabWidget.addTab(self.trajectory_widget, "Trajectory")

        self.stream_widget = StreamWidget(self)
        self.stream_tab_index = self.ui.tabWidget.addTab(self.stream_widget, "Stream")

        self.heatmap_widget = HeatmapWidget(self)
        self.heatmap_tab_index = self.ui.tabWidget.addTab(self.heatmap_widget, "Heatmap")

        self.settings_widget = SettingsWidget(self)
        try:
            actimot_settings = settings.value("ActimotSettings", ActimotSettings.get_default())
            self.settings_widget.set_data(self.actimot_data.dataset, actimot_settings)
        except Exception:
            actimot_settings = ActimotSettings.get_default()
            self.settings_widget.set_data(self.actimot_data.dataset, actimot_settings)

        self.box_selector = BoxSelector(self._select_box, self.settings_widget, self)
        self.box_selector.set_data(actimot_data.dataset)

        self.ui.toolBox.removeItem(0)
        self.ui.toolBox.addItem(self.box_selector, QIcon(":/icons/icons8-dog-tag-16.png"), "Boxes")
        self.ui.toolBox.addItem(self.settings_widget, QIcon(":/icons/icons8-dog-tag-16.png"), "Settings")

        self._update_tabs()

    def _update_tabs(self) -> None:
        is_preprocessed = self.trj_df is not None
        self.ui.tabWidget.setTabVisible(self.plot_tab_index, is_preprocessed)
        self.ui.tabWidget.setTabVisible(self.trajectory_tab_index, is_preprocessed)
        self.ui.tabWidget.setTabVisible(self.stream_tab_index, is_preprocessed)
        self.ui.tabWidget.setTabVisible(self.heatmap_tab_index, is_preprocessed)

    def _select_box(self, selected_box: ActimotAnimalItem) -> None:
        self.trj_df = None
        self.df = self.actimot_data.raw_df[self.actimot_data.raw_df["Box"] == selected_box.box]

        self._update_tabs()

        self.table_view.set_data(self.df, False)
        self.frames_widget.set_data(self.df)

        self.plot_widget.set_data(None)
        self.trajectory_widget.set_data(None)
        self.stream_widget.set_data(None)
        self.heatmap_widget.set_data(None)

    def _preprocess(self) -> None:
        if self.df is None:
            make_toast(
                self,
                "ActiMot",
                "Please select a single box.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        actimot_settings = self.settings_widget.get_settings()
        if (
            actimot_settings.use_smooting
            and actimot_settings.smoothing_window_size is not None
            and actimot_settings.smoothing_window_size % 2 != 1
        ):
            make_toast(
                self,
                "ActiMot",
                "Smoothing window size must be odd.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        self.preprocess_action.setEnabled(False)

        self.toast = make_toast(self, "ActiMot Preprocessing", "Please wait...")
        self.toast.show()

        worker = Worker(calculate_trj, self.df, actimot_settings)
        worker.signals.result.connect(self._work_result)
        worker.signals.finished.connect(self._work_finished)
        TaskManager.start_task(worker)

    def _work_result(self, result: tuple[pd.DataFrame, traja.TrajaDataFrame, float]) -> None:
        df, trj_df, elapsed_time = result

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

        self.table_view.set_data(df, False)

        self.plot_widget.set_variables(self.actimot_data.variables)
        self.plot_widget.set_data(df)

        self.trajectory_widget.set_data(trj_df)
        self.stream_widget.set_data(trj_df)
        self.heatmap_widget.set_data(trj_df)

        self.df = df
        self.trj_df = trj_df

        make_toast(
            self,
            "ActiMot",
            f"ActiMot preprocessing complete in {elapsed_time:.3f} sec.",
            duration=4000,
            preset=ToastPreset.SUCCESS,
            show_duration_bar=True,
            echo_to_logger=True,
        ).show()

    def _work_finished(self) -> None:
        self.toast.hide()
        self.preprocess_action.setEnabled(True)
        self._update_tabs()

    def _destroyed(self) -> None:
        """Save widget settings via QSettings on destruction."""
        settings = QSettings()
        settings.setValue(
            "ActimotSettings",
            self.settings_widget.get_settings(),
        )
