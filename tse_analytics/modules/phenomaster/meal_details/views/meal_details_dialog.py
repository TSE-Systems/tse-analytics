import timeit

import pandas as pd
from loguru import logger
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QCloseEvent, QIcon, QKeyEvent
from PySide6.QtWidgets import QDialog, QFileDialog, QWidget

from tse_analytics.core.data.shared import Variable
from tse_analytics.core.manager import Manager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.modules.phenomaster.meal_details.data.meal_details import MealDetails
from tse_analytics.modules.phenomaster.meal_details.data.meal_details_animal_item import MealDetailsAnimalItem
from tse_analytics.modules.phenomaster.meal_details.interval_meal_processor import process_meal_intervals
from tse_analytics.modules.phenomaster.meal_details.meal_details_settings import MealDetailsSettings
from tse_analytics.modules.phenomaster.meal_details.sequential_meal_processor import process_meal_sequences
from tse_analytics.modules.phenomaster.meal_details.views.meal_details_box_selector import MealDetailsBoxSelector
from tse_analytics.modules.phenomaster.meal_details.views.meal_details_dialog_ui import Ui_MealDetailsDialog
from tse_analytics.modules.phenomaster.meal_details.views.meal_details_plot_widget import MealDetailsPlotWidget
from tse_analytics.modules.phenomaster.meal_details.views.meal_details_settings_widget import MealDetailsSettingsWidget
from tse_analytics.modules.phenomaster.meal_details.views.meal_details_table_view import MealDetailsTableView
from tse_analytics.modules.phenomaster.meal_details.views.meal_episodes_gap_plot_widget import MealEpisodesGapPlotWidget
from tse_analytics.modules.phenomaster.meal_details.views.meal_episodes_intake_plot_widget import (
    MealEpisodesIntakePlotWidget,
)
from tse_analytics.modules.phenomaster.meal_details.views.meal_episodes_offset_plot_widget import (
    MealEpisodesOffsetPlotWidget,
)
from tse_analytics.modules.phenomaster.meal_details.views.meal_intervals_plot_widget import MealIntervalsPlotWidget
from tse_analytics.views.misc.toast import Toast


class MealDetailsDialog(QDialog):
    def __init__(self, meal_details: MealDetails, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_MealDetailsDialog()
        self.ui.setupUi(self)

        settings = QSettings()
        self.restoreGeometry(settings.value("MealDetailsDialog/Geometry"))

        self.meal_details = meal_details

        self.meal_events_table_view = MealDetailsTableView()
        self.meal_events_table_view.set_data(meal_details.raw_df)
        self.ui.tabWidget.addTab(self.meal_events_table_view, "Events")

        self.meal_details_plot_widget = MealDetailsPlotWidget()
        self.meal_details_plot_widget.set_variables(meal_details.variables)
        self.meal_details_plot_widget.set_data(meal_details.raw_df)
        self.ui.tabWidget.addTab(self.meal_details_plot_widget, "Events Plot")

        self.intervals_table_view = MealDetailsTableView()
        self.intervals_table_tab_index = self.ui.tabWidget.addTab(self.intervals_table_view, "Intervals")

        self.intervals_plot_widget = MealIntervalsPlotWidget()
        self.intervals_plot_tab_index = self.ui.tabWidget.addTab(self.intervals_plot_widget, "Intervals Plots")

        self.meal_episodes_table_view = MealDetailsTableView()
        self.episodes_table_tab_index = self.ui.tabWidget.addTab(self.meal_episodes_table_view, "Episodes")

        self.meal_episodes_offset_plot_widget = MealEpisodesOffsetPlotWidget()
        self.episodes_offset_tab_index = self.ui.tabWidget.addTab(
            self.meal_episodes_offset_plot_widget, "Episodes Offset"
        )

        self.meal_episodes_gap_plot_widget = MealEpisodesGapPlotWidget()
        self.episodes_imi_tab_index = self.ui.tabWidget.addTab(self.meal_episodes_gap_plot_widget, "Episodes IMI")

        self.meal_episodes_intake_plot_widget = MealEpisodesIntakePlotWidget()
        self.episodes_intake_tab_index = self.ui.tabWidget.addTab(
            self.meal_episodes_intake_plot_widget, "Episodes Intake"
        )

        self.ui.toolButtonCalculate.clicked.connect(self.__calculate)
        self.ui.toolButtonExport.clicked.connect(self.__export_meal_data)

        self.meal_details_settings_widget = MealDetailsSettingsWidget()
        try:
            meal_details_settings = settings.value("MealDetailsSettings", MealDetailsSettings.get_default())
            self.meal_details_settings_widget.set_data(self.meal_details.dataset, meal_details_settings)
        except Exception:
            meal_details_settings = MealDetailsSettings.get_default()
            self.meal_details_settings_widget.set_data(self.meal_details.dataset, meal_details_settings)

        self.meal_details_box_selector = MealDetailsBoxSelector(self.__filter_boxes, self.meal_details_settings_widget)
        self.meal_details_box_selector.set_data(meal_details.dataset)

        self.ui.toolBox.removeItem(0)
        self.ui.toolBox.addItem(self.meal_details_box_selector, QIcon(":/icons/icons8-dog-tag-16.png"), "Boxes")
        self.ui.toolBox.addItem(self.meal_details_settings_widget, QIcon(":/icons/icons8-dog-tag-16.png"), "Settings")

        self.selected_boxes: list[MealDetailsAnimalItem] = []

        self.meal_events_df: pd.DataFrame | None = self.meal_details.raw_df
        self.meal_episodes_df: pd.DataFrame | None = None
        self.meal_intervals_df: pd.DataFrame | None = None

        self.__update_tabs()
        self.toast = None

    def __update_tabs(self):
        settings = self.meal_details_settings_widget.get_meal_details_settings()
        self.ui.tabWidget.setTabVisible(self.episodes_table_tab_index, settings.sequential_analysis_type)
        self.ui.tabWidget.setTabVisible(self.episodes_offset_tab_index, settings.sequential_analysis_type)
        self.ui.tabWidget.setTabVisible(self.episodes_imi_tab_index, settings.sequential_analysis_type)
        self.ui.tabWidget.setTabVisible(self.episodes_intake_tab_index, settings.sequential_analysis_type)

        self.ui.tabWidget.setTabVisible(self.intervals_table_tab_index, not settings.sequential_analysis_type)
        self.ui.tabWidget.setTabVisible(self.intervals_plot_tab_index, not settings.sequential_analysis_type)

    def __filter_boxes(self, selected_boxes: list[MealDetailsAnimalItem]):
        self.selected_boxes = selected_boxes
        self.__filter()

    def __get_variables_subset(self) -> dict[str, Variable]:
        variables_subset: dict[str, Variable] = {}
        if "Drink1" in self.meal_details.variables:
            variables_subset["Drink1"] = self.meal_details.variables["Drink1"]
        if "Feed1" in self.meal_details.variables:
            variables_subset["Feed1"] = self.meal_details.variables["Feed1"]
        if "Drink2" in self.meal_details.variables:
            variables_subset["Drink2"] = self.meal_details.variables["Drink2"]
        if "Feed2" in self.meal_details.variables:
            variables_subset["Feed2"] = self.meal_details.variables["Feed2"]
        return variables_subset

    def __filter(self):
        events_df = self.meal_events_df
        episodes_df = self.meal_episodes_df
        intervals_df = self.meal_intervals_df

        if len(self.selected_boxes) > 0:
            box_numbers = [b.box for b in self.selected_boxes]
            events_df = events_df[events_df["Box"].isin(box_numbers)]

            if episodes_df is not None:
                episodes_df = episodes_df[episodes_df["Box"].isin(box_numbers)]

            if intervals_df is not None:
                intervals_df = intervals_df[intervals_df["Box"].isin(box_numbers)]

        self.meal_events_table_view.set_data(events_df)
        self.meal_details_plot_widget.set_data(events_df)

        if episodes_df is not None:
            self.meal_episodes_table_view.set_data(episodes_df)

        if intervals_df is not None:
            self.intervals_table_view.set_data(intervals_df)
            self.intervals_plot_widget.set_data(intervals_df, self.__get_variables_subset())

    def __calculate(self):
        self.ui.toolButtonCalculate.setEnabled(False)
        self.ui.toolButtonExport.setEnabled(False)

        self.toast = Toast(text="Processing...", parent=self, duration=None)
        self.toast.show_toast()

        meal_details_settings = self.meal_details_settings_widget.get_meal_details_settings()
        diets_dict = self.meal_details_box_selector.get_diets_dict()

        if meal_details_settings.sequential_analysis_type:
            worker = Worker(self.__do_sequential_analysis, meal_details_settings, diets_dict)
            worker.signals.finished.connect(self.__sequential_analysis_finished)
        else:
            worker = Worker(self.__do_interval_analysis, meal_details_settings, diets_dict)
            worker.signals.finished.connect(self.__interval_analysis_finished)
        Manager.threadpool.start(worker)

    def __do_sequential_analysis(
        self,
        meal_details_settings: MealDetailsSettings,
        diets_dict: dict[int, float],
    ):
        tic = timeit.default_timer()

        self.meal_events_df, self.meal_episodes_df = process_meal_sequences(
            self.meal_details, meal_details_settings, diets_dict
        )

        logger.info(f"Meal analysis complete: {timeit.default_timer() - tic} sec")

    def __sequential_analysis_finished(self):
        variables_subset = self.__get_variables_subset()

        self.meal_events_table_view.set_data(self.meal_events_df)
        self.meal_episodes_table_view.set_data(self.meal_episodes_df)

        self.meal_episodes_offset_plot_widget.set_data(self.meal_episodes_df, variables_subset)
        self.meal_episodes_gap_plot_widget.set_data(self.meal_episodes_df, variables_subset)
        self.meal_episodes_intake_plot_widget.set_data(self.meal_episodes_df, variables_subset)

        self.__update_tabs()
        self.ui.toolButtonExport.setEnabled(True)
        self.ui.toolButtonCalculate.setEnabled(True)
        self.toast.close_toast()

    def __do_interval_analysis(
        self,
        meal_details_settings: MealDetailsSettings,
        diets_dict: dict[int, float],
    ):
        tic = timeit.default_timer()

        self.meal_intervals_df = process_meal_intervals(self.meal_details, meal_details_settings, diets_dict)

        logger.info(f"Meal analysis complete: {timeit.default_timer() - tic} sec")

    def __interval_analysis_finished(self):
        variables_subset = self.__get_variables_subset()

        self.intervals_table_view.set_data(self.meal_intervals_df)
        self.intervals_plot_widget.set_data(self.meal_intervals_df, variables_subset)

        self.__update_tabs()
        self.ui.toolButtonExport.setEnabled(True)
        self.ui.toolButtonCalculate.setEnabled(True)
        self.toast.close_toast()

    def __export_meal_data(self):
        meal_details_settings = self.meal_details_settings_widget.get_meal_details_settings()
        if meal_details_settings.sequential_analysis_type and self.meal_episodes_df is not None:
            filename, _ = QFileDialog.getSaveFileName(self, "Export to CSV", "MealEpisodes", "CSV Files (*.csv)")
            if filename:
                self.meal_episodes_df.to_csv(filename, sep=";", index=False)
        elif self.meal_intervals_df is not None:
            filename, _ = QFileDialog.getSaveFileName(self, "Export to CSV", "MealIntervals", "CSV Files (*.csv)")
            if filename:
                self.meal_intervals_df.to_csv(filename, sep=";", index=False)

    def hideEvent(self, event: QCloseEvent) -> None:
        settings = QSettings()
        settings.setValue("MealDetailsDialog/Geometry", self.saveGeometry())

        meal_details_settings = self.meal_details_settings_widget.get_meal_details_settings()
        settings.setValue("MealDetailsSettings", meal_details_settings)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Escape:
            return
        super().keyPressEvent(event)
