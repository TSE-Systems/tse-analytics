import timeit
from datetime import datetime

import pandas as pd
from PySide6.QtCore import QSettings, Qt, QSize
from PySide6.QtGui import QCloseEvent, QIcon
from PySide6.QtWidgets import QWidget, QToolBar
from loguru import logger

from tse_analytics.core import manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.workers.task_manager import TaskManager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.modules.phenomaster.io import tse_import_settings
from tse_analytics.modules.phenomaster.submodules.drinkfeed.data.drinkfeed_animal_item import DrinkFeedAnimalItem
from tse_analytics.modules.phenomaster.submodules.drinkfeed.data.drinkfeed_data import DrinkFeedData
from tse_analytics.modules.phenomaster.submodules.drinkfeed.drinkfeed_settings import DrinkFeedSettings
from tse_analytics.modules.phenomaster.submodules.drinkfeed.interval_processor import process_drinkfeed_intervals
from tse_analytics.modules.phenomaster.submodules.drinkfeed.sequential_processor2 import process_drinkfeed_sequences2
from tse_analytics.modules.phenomaster.submodules.drinkfeed.views.drinkfeed_animal_selector import (
    DrinkFeedAnimalSelector,
)
from tse_analytics.modules.phenomaster.submodules.drinkfeed.views.drinkfeed_dialog_ui import Ui_DrinkFeedDialog
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
from tse_analytics.modules.phenomaster.submodules.drinkfeed.views.drinkfeed_plot_widget import DrinkFeedPlotWidget
from tse_analytics.modules.phenomaster.submodules.drinkfeed.views.drinkfeed_settings_widget import (
    DrinkFeedSettingsWidget,
)
from tse_analytics.modules.phenomaster.submodules.drinkfeed.views.drinkfeed_table_view import DrinkFeedTableView


class DrinkFeedDialog(QWidget):
    def __init__(self, drinkfeed_data: DrinkFeedData, parent: QWidget):
        super().__init__(parent)

        self.ui = Ui_DrinkFeedDialog()
        self.ui.setupUi(self)

        self.setWindowFlags(
            Qt.WindowType.Window
            # | Qt.WindowType.CustomizeWindowHint
            # | Qt.WindowType.WindowTitleHint
            # | Qt.WindowType.WindowCloseButtonHint
        )

        settings = QSettings()
        self.restoreGeometry(settings.value("DrinkFeedDialog/Geometry"))

        self.drinkfeed_data = drinkfeed_data
        self.selected_animals: list[DrinkFeedAnimalItem] = []

        self.raw_df = self.drinkfeed_data.raw_df
        if (
            self.drinkfeed_data.name == tse_import_settings.DRINKFEED_BIN_TABLE
            # TODO: remove later
            or self.drinkfeed_data.name == "DrinkFeed Data"
        ):
            self.raw_long_df = pd.melt(
                self.raw_df,
                id_vars=["DateTime", "Animal", "Box"],
                var_name="Sensor",
                value_name="Value",
            )
            self.raw_long_df.sort_values(by=["DateTime"], inplace=True)
            self.raw_long_df.reset_index(drop=True, inplace=True)
        else:
            self.raw_long_df = self.raw_df

        self.events_df: pd.DataFrame | None = None
        self.episodes_df: pd.DataFrame | None = None
        self.intervals_df: pd.DataFrame | None = None

        self.toast = None

        # Setup toolbar
        toolbar = QToolBar(
            "Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.calculate_action = toolbar.addAction(QIcon(":/icons/icons8-analyze-16.png"), "Calculate")
        self.calculate_action.triggered.connect(self._calculate)
        self.add_datatable_action = toolbar.addAction(QIcon(":/icons/icons8-insert-table-16.png"), "Add Datatable...")
        self.add_datatable_action.setEnabled(False)
        self.add_datatable_action.triggered.connect(self._add_datatable)
        self.ui.verticalLayout.insertWidget(0, toolbar)

        self.raw_table_view = DrinkFeedTableView()
        self.raw_table_view.set_data(self.raw_df)
        self.ui.tabWidget.addTab(self.raw_table_view, "Raw Data")

        self.raw_plot_widget = DrinkFeedPlotWidget()
        self.raw_plot_widget.set_data(self.raw_long_df)
        self.raw_plot_widget.set_variables(drinkfeed_data.variables)
        self.ui.tabWidget.addTab(self.raw_plot_widget, "Raw Data Plot")

        self.intervals_table_view = DrinkFeedTableView()
        self.intervals_table_tab_index = self.ui.tabWidget.addTab(self.intervals_table_view, "Intervals")

        self.intervals_plot_widget = DrinkFeedIntervalsPlotWidget()
        self.intervals_plot_tab_index = self.ui.tabWidget.addTab(self.intervals_plot_widget, "Intervals Plots")

        self.events_table_view = DrinkFeedTableView()
        self.events_table_tab_index = self.ui.tabWidget.addTab(self.events_table_view, "Events")

        self.episodes_table_view = DrinkFeedTableView()
        self.episodes_table_tab_index = self.ui.tabWidget.addTab(self.episodes_table_view, "Episodes")

        self.episodes_offset_plot_widget = DrinkFeedEpisodesOffsetPlotWidget()
        self.episodes_offset_tab_index = self.ui.tabWidget.addTab(self.episodes_offset_plot_widget, "Episodes Offset")

        self.episodes_gap_plot_widget = DrinkFeedEpisodesGapPlotWidget()
        self.episodes_imi_tab_index = self.ui.tabWidget.addTab(self.episodes_gap_plot_widget, "Episodes IMI")

        self.episodes_intake_plot_widget = DrinkFeedEpisodesIntakePlotWidget()
        self.episodes_intake_tab_index = self.ui.tabWidget.addTab(self.episodes_intake_plot_widget, "Episodes Intake")

        self.drinkfeed_settings_widget = DrinkFeedSettingsWidget()
        try:
            drinkfeed_settings = settings.value("DrinkFeedSettings", DrinkFeedSettings.get_default())
            self.drinkfeed_settings_widget.set_data(self.drinkfeed_data.dataset, drinkfeed_settings)
        except Exception:
            drinkfeed_settings = DrinkFeedSettings.get_default()
            self.drinkfeed_settings_widget.set_data(self.drinkfeed_data.dataset, drinkfeed_settings)

        self.drinkfeed_animal_selector = DrinkFeedAnimalSelector(self._filter_animals, self.drinkfeed_settings_widget)
        self.drinkfeed_animal_selector.set_data(drinkfeed_data.dataset)

        self.ui.toolBox.removeItem(0)
        self.ui.toolBox.addItem(
            self.drinkfeed_animal_selector, QIcon(":/icons/icons8-rat-silhouette-16.png"), "Animals"
        )
        self.ui.toolBox.addItem(self.drinkfeed_settings_widget, QIcon(":/icons/icons8-settings-16.png"), "Settings")

        self._update_tabs()

    def _update_tabs(self):
        settings = self.drinkfeed_settings_widget.get_drinkfeed_settings()
        show_episodes = settings.sequential_analysis_type and self.episodes_df is not None
        self.ui.tabWidget.setTabVisible(self.events_table_tab_index, show_episodes)
        self.ui.tabWidget.setTabVisible(self.episodes_table_tab_index, show_episodes)
        self.ui.tabWidget.setTabVisible(self.episodes_offset_tab_index, show_episodes)
        self.ui.tabWidget.setTabVisible(self.episodes_imi_tab_index, show_episodes)
        self.ui.tabWidget.setTabVisible(self.episodes_intake_tab_index, show_episodes)
        show_intervals = not settings.sequential_analysis_type and self.intervals_df is not None
        self.ui.tabWidget.setTabVisible(self.intervals_table_tab_index, show_intervals)
        self.ui.tabWidget.setTabVisible(self.intervals_plot_tab_index, show_intervals)

    def _filter_animals(self, selected_animals: list[DrinkFeedAnimalItem]):
        self.selected_animals = selected_animals

        raw_long_df = self.raw_long_df
        events_df = self.events_df
        episodes_df = self.episodes_df
        intervals_df = self.intervals_df

        if len(self.selected_animals) > 0:
            animal_ids = [item.animal for item in self.selected_animals]

            raw_long_df = raw_long_df[raw_long_df["Animal"].isin(animal_ids)]

            if events_df is not None:
                events_df = events_df[events_df["Animal"].isin(animal_ids)]
            if episodes_df is not None:
                episodes_df = episodes_df[episodes_df["Animal"].isin(animal_ids)]
            if intervals_df is not None:
                intervals_df = intervals_df[intervals_df["Animal"].isin(animal_ids)]

        self.raw_plot_widget.set_data(raw_long_df)

        if events_df is not None:
            self.events_table_view.set_data(events_df)

        if episodes_df is not None:
            self.episodes_table_view.set_data(episodes_df)

        if intervals_df is not None:
            self.intervals_table_view.set_data(intervals_df)
            self.intervals_plot_widget.set_data(intervals_df, self.drinkfeed_data.variables)

    def _calculate(self):
        self.calculate_action.setEnabled(False)
        self.add_datatable_action.setEnabled(False)

        self.toast = make_toast(self, "DrinkFeed Analysis", "Processing...")
        self.toast.show()

        drinkfeed_settings = self.drinkfeed_settings_widget.get_drinkfeed_settings()
        diets_dict = self.drinkfeed_animal_selector.get_diets_dict()

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

        self.events_df, self.episodes_df = process_drinkfeed_sequences2(self.drinkfeed_data, settings, diets_dict)
        # self.events_df, self.episodes_df = process_drinkfeed_sequences(self.drinkfeed_data, settings, diets_dict)

        logger.info(f"DrinkFeed analysis complete: {timeit.default_timer() - tic} sec")

    def _sequential_analysis_finished(self):
        self.events_table_view.set_data(self.events_df)
        self.episodes_table_view.set_data(self.episodes_df)

        self.episodes_offset_plot_widget.set_data(self.episodes_df, self.drinkfeed_data.variables)
        self.episodes_gap_plot_widget.set_data(self.episodes_df, self.drinkfeed_data.variables)
        self.episodes_intake_plot_widget.set_data(self.episodes_df, self.drinkfeed_data.variables)

        self._update_tabs()
        self.add_datatable_action.setEnabled(True)
        self.calculate_action.setEnabled(True)
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
        self.intervals_table_view.set_data(self.intervals_df)
        self.intervals_plot_widget.set_data(self.intervals_df, self.drinkfeed_data.variables)

        self._update_tabs()
        self.add_datatable_action.setEnabled(True)
        self.calculate_action.setEnabled(True)
        self.toast.hide()

    def _add_datatable(self):
        settings = self.drinkfeed_settings_widget.get_drinkfeed_settings()
        now = datetime.now()
        now_string = now.strftime("%Y-%m-%d %H:%M:%S")

        variables = self.drinkfeed_data.variables

        if settings.sequential_analysis_type and self.episodes_df is not None:
            datatable = Datatable(
                self.drinkfeed_data.dataset,
                f"DrinkFeedEpisodes [{now_string}]",
                "Drink/Feed episodes",
                variables,
                self.episodes_df,
                None,
            )
            manager.add_datatable(datatable)
        elif self.intervals_df is not None:
            timedelta = pd.Timedelta(
                hours=settings.fixed_interval.hour,
                minutes=settings.fixed_interval.minute,
                seconds=settings.fixed_interval.second,
            )
            datatable = Datatable(
                self.drinkfeed_data.dataset,
                f"DrinkFeedIntervals [{now_string}]",
                "Drink/Feed intervals",
                variables,
                self.intervals_df,
                timedelta,
            )
            manager.add_datatable(datatable)

    def closeEvent(self, event: QCloseEvent) -> None:
        settings = QSettings()
        settings.setValue("DrinkFeedDialog/Geometry", self.saveGeometry())

        drinkfeed_settings = self.drinkfeed_settings_widget.get_drinkfeed_settings()
        settings.setValue("DrinkFeedSettings", drinkfeed_settings)
