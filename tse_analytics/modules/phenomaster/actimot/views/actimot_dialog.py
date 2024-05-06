import timeit

import pandas as pd
import traja
from loguru import logger
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QCloseEvent, QIcon, QKeyEvent
from PySide6.QtWidgets import QDialog, QFileDialog, QWidget

from tse_analytics.modules.phenomaster.actimot.actimot_settings import ActimotSettings
from tse_analytics.modules.phenomaster.actimot.data.actimot_animal_item import ActimotAnimalItem
from tse_analytics.modules.phenomaster.actimot.data.actimot_details import ActimotDetails
from tse_analytics.modules.phenomaster.actimot.views.actimot_box_selector import ActimotBoxSelector
from tse_analytics.modules.phenomaster.actimot.views.actimot_dialog_ui import Ui_ActimotDialog
from tse_analytics.modules.phenomaster.actimot.views.actimot_frames_widget import ActimotFramesWidget
from tse_analytics.modules.phenomaster.actimot.views.actimot_heatmap_plot_widget import ActimotHeatmapPlotWidget
from tse_analytics.modules.phenomaster.actimot.views.actimot_plot_widget import ActimotPlotWidget
from tse_analytics.modules.phenomaster.actimot.views.actimot_settings_widget import ActimotSettingsWidget
from tse_analytics.modules.phenomaster.actimot.views.actimot_stream_plot_widget import ActimotStreamPlotWidget
from tse_analytics.modules.phenomaster.actimot.views.actimot_table_view import ActimotTableView
from tse_analytics.modules.phenomaster.actimot.views.actimot_trajectory_plot_widget import ActimotTrajectoryPlotWidget
from tse_analytics.views.misc.toast import Toast


class ActimotDialog(QDialog):
    def __init__(self, actimot_details: ActimotDetails, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_ActimotDialog()
        self.ui.setupUi(self)

        settings = QSettings()
        self.restoreGeometry(settings.value("ActimotDialog/Geometry"))

        self.actimot_details = actimot_details

        self.actimot_table_view = ActimotTableView()
        self.actimot_table_view.set_data(actimot_details.raw_df)
        self.ui.tabWidget.addTab(self.actimot_table_view, "Events")

        self.actimot_plot_widget = ActimotPlotWidget()
        self.actimot_plot_widget.set_variables(actimot_details.variables)
        self.actimot_plot_widget.set_data(actimot_details.raw_df)
        self.ui.tabWidget.addTab(self.actimot_plot_widget, "Events Plot")

        self.actimot_frames_widget = ActimotFramesWidget()
        self.actimot_frames_widget.set_data(actimot_details.raw_df)
        self.ui.tabWidget.addTab(self.actimot_frames_widget, "Frames")

        self.actimot_trajectory_plot_widget = ActimotTrajectoryPlotWidget()
        self.ui.tabWidget.addTab(self.actimot_trajectory_plot_widget, "Trajectory")

        self.actimot_stream_plot_widget = ActimotStreamPlotWidget()
        self.ui.tabWidget.addTab(self.actimot_stream_plot_widget, "Stream")

        self.actimot_heatmap_plot_widget = ActimotHeatmapPlotWidget()
        self.ui.tabWidget.addTab(self.actimot_heatmap_plot_widget, "Heatmap")

        self.ui.toolButtonCalculate.clicked.connect(self.__calculate)
        self.ui.toolButtonExport.clicked.connect(self.__export_data)

        self.actimot_settings_widget = ActimotSettingsWidget()
        try:
            actimot_settings = settings.value("ActimotSettings", ActimotSettings.get_default())
            self.actimot_settings_widget.set_data(self.actimot_details.dataset, actimot_settings)
        except Exception:
            actimot_settings = ActimotSettings.get_default()
            self.actimot_settings_widget.set_data(self.actimot_details.dataset, actimot_settings)

        self.actimot_box_selector = ActimotBoxSelector(self.__filter_boxes, self.actimot_settings_widget)
        self.actimot_box_selector.set_data(actimot_details.dataset)

        self.ui.toolBox.removeItem(0)
        self.ui.toolBox.addItem(self.actimot_box_selector, QIcon(":/icons/icons8-dog-tag-16.png"), "Boxes")
        self.ui.toolBox.addItem(self.actimot_settings_widget, QIcon(":/icons/icons8-dog-tag-16.png"), "Settings")

        self.selected_boxes: list[ActimotAnimalItem] = []

        self.actimot_events_df = self.actimot_details.raw_df

    def __filter_boxes(self, selected_boxes: list[ActimotAnimalItem]):
        self.selected_boxes = selected_boxes
        self.__filter()

    def __filter(self):
        events_df = self.actimot_events_df

        if len(self.selected_boxes) > 0:
            box_numbers = [b.box for b in self.selected_boxes]
            events_df = events_df[events_df["Box"].isin(box_numbers)]

        self.actimot_table_view.set_data(events_df)
        self.actimot_plot_widget.set_data(events_df)

    def __calculate(self):
        tic = timeit.default_timer()

        actimot_settings = self.actimot_settings_widget.get_settings()

        new_df = self.actimot_events_df[["DateTime", "X (cm)", "Y (cm)"]]
        new_df.rename(columns={"DateTime": "time", "X (cm)": "x", "Y (cm)": "y"}, inplace=True)
        new_df = new_df.dropna(subset=["x", "y"])

        trj_df = traja.from_df(df=new_df)
        trj_df.spatial_units = "cm"

        preprocessed_trj = trj_df.copy()
        preprocessed_trj["time"] = preprocessed_trj["time"].astype("int64") / 10 ** 9
        preprocessed_trj = traja.get_derivatives(preprocessed_trj)

        df = pd.concat([new_df, preprocessed_trj], ignore_index=False, axis="columns")

        self.actimot_table_view.set_data(df)

        self.actimot_trajectory_plot_widget.set_data(trj_df)
        self.actimot_stream_plot_widget.set_data(trj_df)
        self.actimot_heatmap_plot_widget.set_data(trj_df)

        self.ui.toolButtonExport.setEnabled(True)

        logger.info(f"Actimot analysis complete: {timeit.default_timer() - tic} sec")
        Toast(text="Actimot analysis complete.", parent=self, duration=4000).show_toast()

    def __export_data(self):
        settings = self.actimot_settings_widget.get_settings()
        filename, _ = QFileDialog.getSaveFileName(self, "Export to CSV", "ActimotEvents", "CSV Files (*.csv)")
        if filename:
            self.actimot_events_df.to_csv(filename, sep=";", index=False)

    def hideEvent(self, event: QCloseEvent) -> None:
        settings = QSettings()
        settings.setValue("ActimotDialog/Geometry", self.saveGeometry())

        actimot_settings = self.actimot_settings_widget.get_settings()
        settings.setValue("ActimotSettings", actimot_settings)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Escape:
            return
        super().keyPressEvent(event)
