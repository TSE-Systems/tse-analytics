import timeit

import pandas as pd
from loguru import logger
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QCloseEvent, QIcon, QKeyEvent
from PySide6.QtWidgets import QDialog, QFileDialog, QWidget

from tse_analytics.core.data.shared import Variable
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.workers.task_manager import TaskManager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.modules.phenomaster.submodules.drinkfeed.data.drinkfeed_data import DrinkFeedData
from tse_analytics.modules.phenomaster.submodules.drinkfeed.data.drinkfeed_animal_item import DrinkFeedAnimalItem
from tse_analytics.modules.phenomaster.submodules.drinkfeed.interval_processor import process_drinkfeed_intervals
from tse_analytics.modules.phenomaster.submodules.drinkfeed.drinkfeed_settings import DrinkFeedSettings
from tse_analytics.modules.phenomaster.submodules.drinkfeed.sequential_processor import process_drinkfeed_sequences
from tse_analytics.modules.phenomaster.submodules.drinkfeed.views.drinkfeed_box_selector import (
    DrinkFeedBoxSelector,
)
from tse_analytics.modules.phenomaster.submodules.drinkfeed.views.drinkfeed_dialog_ui import Ui_DrinkFeedDialog
from tse_analytics.modules.phenomaster.submodules.drinkfeed.views.drinkfeed_plot_widget import DrinkFeedPlotWidget
from tse_analytics.modules.phenomaster.submodules.drinkfeed.views.drinkfeed_settings_widget import (
    DrinkFeedSettingsWidget,
)
from tse_analytics.modules.phenomaster.submodules.drinkfeed.views.drinkfeed_table_view import DrinkFeedTableView
from tse_analytics.modules.phenomaster.submodules.drinkfeed.views.drinkfeed_episodes_gap_plot_widget import (
    DrinkFeedEpisodesGapPlotWidget,
)
from tse_analytics.modules.phenomaster.submodules.drinkfeed.views.drinkfeed_episodes_intake_plot_widget import (
    DrinkFeedEpisodesIntakePlotWidget,
)
from tse_analytics.modules.phenomaster.submodules.drinkfeed.views.drinkfeed_episodes_offset_plot_widget import (
    DrinkFeedEpisodesOffsetPlotWidget,
)
from tse_analytics.modules.phenomaster.submodules.drinkfeed.views.drinkfeed_intervals_plot_widget import (
    DrinkFeedIntervalsPlotWidget,
)


class DrinkFeedDialog(QDialog):
    def __init__(self, drinkfeed_data: DrinkFeedData, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_DrinkFeedDialog()
        self.ui.setupUi(self)

        settings = QSettings()
        self.restoreGeometry(settings.value("DrinkFeedDialog/Geometry"))

        self.drinkfeed_data = drinkfeed_data

        self.events_table_view = DrinkFeedTableView()
        self.events_table_view.set_data(drinkfeed_data.raw_df)
        self.ui.tabWidget.addTab(self.events_table_view, "Events")

        self.drinkfeed_plot_widget = DrinkFeedPlotWidget()
        self.drinkfeed_plot_widget.set_variables(drinkfeed_data.variables)
        self.drinkfeed_plot_widget.set_data(drinkfeed_data.raw_df)
        self.ui.tabWidget.addTab(self.drinkfeed_plot_widget, "Events Plot")

        self.intervals_table_view = DrinkFeedTableView()
        self.intervals_table_tab_index = self.ui.tabWidget.addTab(self.intervals_table_view, "Intervals")

        self.intervals_plot_widget = DrinkFeedIntervalsPlotWidget()
        self.intervals_plot_tab_index = self.ui.tabWidget.addTab(self.intervals_plot_widget, "Intervals Plots")

        self.episodes_table_view = DrinkFeedTableView()
        self.episodes_table_tab_index = self.ui.tabWidget.addTab(self.episodes_table_view, "Episodes")

        self.episodes_offset_plot_widget = DrinkFeedEpisodesOffsetPlotWidget()
        self.episodes_offset_tab_index = self.ui.tabWidget.addTab(self.episodes_offset_plot_widget, "Episodes Offset")

        self.episodes_gap_plot_widget = DrinkFeedEpisodesGapPlotWidget()
        self.episodes_imi_tab_index = self.ui.tabWidget.addTab(self.episodes_gap_plot_widget, "Episodes IMI")

        self.episodes_intake_plot_widget = DrinkFeedEpisodesIntakePlotWidget()
        self.episodes_intake_tab_index = self.ui.tabWidget.addTab(self.episodes_intake_plot_widget, "Episodes Intake")

        self.ui.toolButtonCalculate.clicked.connect(self._calculate)
        self.ui.toolButtonExport.clicked.connect(self._export_data)

        self.drinkfeed_settings_widget = DrinkFeedSettingsWidget()
        try:
            drinkfeed_settings = settings.value("DrinkFeedSettings", DrinkFeedSettings.get_default())
            self.drinkfeed_settings_widget.set_data(self.drinkfeed_data.dataset, drinkfeed_settings)
        except Exception:
            drinkfeed_settings = DrinkFeedSettings.get_default()
            self.drinkfeed_settings_widget.set_data(self.drinkfeed_data.dataset, drinkfeed_settings)

        self.drinkfeed_box_selector = DrinkFeedBoxSelector(self._filter_boxes, self.drinkfeed_settings_widget)
        self.drinkfeed_box_selector.set_data(drinkfeed_data.dataset)

        self.ui.toolBox.removeItem(0)
        self.ui.toolBox.addItem(self.drinkfeed_box_selector, QIcon(":/icons/icons8-dog-tag-16.png"), "Boxes")
        self.ui.toolBox.addItem(self.drinkfeed_settings_widget, QIcon(":/icons/icons8-dog-tag-16.png"), "Settings")

        self.selected_boxes: list[DrinkFeedAnimalItem] = []

        self.events_df: pd.DataFrame | None = self.drinkfeed_data.raw_df
        self.episodes_df: pd.DataFrame | None = None
        self.intervals_df: pd.DataFrame | None = None

        self._update_tabs()
        self.toast = None

    def _update_tabs(self):
        settings = self.drinkfeed_settings_widget.get_drinkfeed_settings()
        self.ui.tabWidget.setTabVisible(self.episodes_table_tab_index, settings.sequential_analysis_type)
        self.ui.tabWidget.setTabVisible(self.episodes_offset_tab_index, settings.sequential_analysis_type)
        self.ui.tabWidget.setTabVisible(self.episodes_imi_tab_index, settings.sequential_analysis_type)
        self.ui.tabWidget.setTabVisible(self.episodes_intake_tab_index, settings.sequential_analysis_type)

        self.ui.tabWidget.setTabVisible(self.intervals_table_tab_index, not settings.sequential_analysis_type)
        self.ui.tabWidget.setTabVisible(self.intervals_plot_tab_index, not settings.sequential_analysis_type)

    def _filter_boxes(self, selected_boxes: list[DrinkFeedAnimalItem]):
        self.selected_boxes = selected_boxes

        events_df = self.events_df
        episodes_df = self.episodes_df
        intervals_df = self.intervals_df

        if len(self.selected_boxes) > 0:
            box_numbers = [b.box for b in self.selected_boxes]
            events_df = events_df[events_df["Box"].isin(box_numbers)]

            if episodes_df is not None:
                episodes_df = episodes_df[episodes_df["Box"].isin(box_numbers)]

            if intervals_df is not None:
                intervals_df = intervals_df[intervals_df["Box"].isin(box_numbers)]

        self.events_table_view.set_data(events_df)
        self.drinkfeed_plot_widget.set_data(events_df)

        if episodes_df is not None:
            self.episodes_table_view.set_data(episodes_df)

        if intervals_df is not None:
            self.intervals_table_view.set_data(intervals_df)
            self.intervals_plot_widget.set_data(intervals_df, self._get_variables_subset())

    def _get_variables_subset(self) -> dict[str, Variable]:
        variables_subset: dict[str, Variable] = {}
        if "Drink1" in self.drinkfeed_data.variables:
            variables_subset["Drink1"] = self.drinkfeed_data.variables["Drink1"]
        if "Feed1" in self.drinkfeed_data.variables:
            variables_subset["Feed1"] = self.drinkfeed_data.variables["Feed1"]
        if "Drink2" in self.drinkfeed_data.variables:
            variables_subset["Drink2"] = self.drinkfeed_data.variables["Drink2"]
        if "Feed2" in self.drinkfeed_data.variables:
            variables_subset["Feed2"] = self.drinkfeed_data.variables["Feed2"]
        if "Drink" in self.drinkfeed_data.variables:
            variables_subset["Drink"] = self.drinkfeed_data.variables["Drink"]
        if "Feed" in self.drinkfeed_data.variables:
            variables_subset["Feed"] = self.drinkfeed_data.variables["Feed"]
        return variables_subset

    def _calculate(self):
        self.ui.toolButtonCalculate.setEnabled(False)
        self.ui.toolButtonExport.setEnabled(False)

        self.toast = make_toast(self, "DrinkFeed Analysis", "Processing...")
        self.toast.show()

        drinkfeed_settings = self.drinkfeed_settings_widget.get_drinkfeed_settings()
        diets_dict = self.drinkfeed_box_selector.get_diets_dict()

        if drinkfeed_settings.sequential_analysis_type:
            worker = Worker(self._do_sequential_analysis, drinkfeed_settings, diets_dict)
            worker.signals.finished.connect(self._sequential_analysis_finished)
        else:
            worker = Worker(self._do_interval_analysis, drinkfeed_settings, diets_dict)
            worker.signals.finished.connect(self._interval_analysis_finished)
        TaskManager.start_task(worker)

    def _do_sequential_analysis(
        self,
        settings: DrinkFeedSettings,
        diets_dict: dict[str, float],
    ):
        tic = timeit.default_timer()

        self.events_df, self.episodes_df = process_drinkfeed_sequences(self.drinkfeed_data, settings, diets_dict)

        logger.info(f"DrinkFeed analysis complete: {timeit.default_timer() - tic} sec")

    def _sequential_analysis_finished(self):
        variables_subset = self._get_variables_subset()

        self.events_table_view.set_data(self.events_df)
        self.episodes_table_view.set_data(self.episodes_df)

        self.episodes_offset_plot_widget.set_data(self.episodes_df, variables_subset)
        self.episodes_gap_plot_widget.set_data(self.episodes_df, variables_subset)
        self.episodes_intake_plot_widget.set_data(self.episodes_df, variables_subset)

        self._update_tabs()
        self.ui.toolButtonExport.setEnabled(True)
        self.ui.toolButtonCalculate.setEnabled(True)
        self.toast.hide()

    def _do_interval_analysis(
        self,
        settings: DrinkFeedSettings,
        diets_dict: dict[int, float],
    ):
        tic = timeit.default_timer()

        self.intervals_df = process_drinkfeed_intervals(self.drinkfeed_data, settings, diets_dict)

        logger.info(f"DrinkFeed analysis complete: {timeit.default_timer() - tic} sec")

    def _interval_analysis_finished(self):
        variables_subset = self._get_variables_subset()

        self.intervals_table_view.set_data(self.intervals_df)
        self.intervals_plot_widget.set_data(self.intervals_df, variables_subset)

        self._update_tabs()
        self.ui.toolButtonExport.setEnabled(True)
        self.ui.toolButtonCalculate.setEnabled(True)
        self.toast.hide()

    def _export_data(self):
        settings = self.drinkfeed_settings_widget.get_drinkfeed_settings()
        if settings.sequential_analysis_type and self.episodes_df is not None:
            filename, _ = QFileDialog.getSaveFileName(self, "Export to CSV", "DrinkFeedEpisodes", "CSV Files (*.csv)")
            if filename:
                self.episodes_df.to_csv(filename, sep=";", index=False)
        elif self.intervals_df is not None:
            filename, _ = QFileDialog.getSaveFileName(self, "Export to CSV", "DrinkFeedIntervals", "CSV Files (*.csv)")
            if filename:
                self.intervals_df.to_csv(filename, sep=";", index=False)

    def hideEvent(self, event: QCloseEvent) -> None:
        settings = QSettings()
        settings.setValue("DrinkFeedDialog/Geometry", self.saveGeometry())

        drinkfeed_settings = self.drinkfeed_settings_widget.get_drinkfeed_settings()
        settings.setValue("DrinkFeedSettings", drinkfeed_settings)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Escape:
            return
        super().keyPressEvent(event)
