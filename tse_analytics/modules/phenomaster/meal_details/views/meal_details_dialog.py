import timeit

import pandas as pd
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QCloseEvent, QIcon, QKeyEvent
from PySide6.QtWidgets import QDialog, QWidget, QFileDialog
from loguru import logger

from tse_analytics.core.data.shared import Variable
from tse_analytics.modules.phenomaster.meal_details.data.meal_details import MealDetails
from tse_analytics.modules.phenomaster.meal_details.data.meal_details_box import MealDetailsBox
from tse_analytics.modules.phenomaster.meal_details.meal_details_processor import process_meal_details
from tse_analytics.modules.phenomaster.meal_details.meal_details_settings import MealDetailsSettings
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
from tse_analytics.views.misc.toast import Toast


class MealDetailsDialog(QDialog):
    """MealDetails Dialog"""

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

        self.meal_episodes_table_view = MealDetailsTableView()
        self.ui.tabWidget.addTab(self.meal_episodes_table_view, "Episodes")

        self.meal_episodes_offset_plot_widget = MealEpisodesOffsetPlotWidget()
        self.ui.tabWidget.addTab(self.meal_episodes_offset_plot_widget, "Episodes Offset")

        self.meal_episodes_gap_plot_widget = MealEpisodesGapPlotWidget()
        self.ui.tabWidget.addTab(self.meal_episodes_gap_plot_widget, "Episodes IMI")

        self.meal_episodes_intake_plot_widget = MealEpisodesIntakePlotWidget()
        self.ui.tabWidget.addTab(self.meal_episodes_intake_plot_widget, "Episodes Intake")

        self.ui.toolBox.removeItem(0)

        self.ui.toolButtonCalculate.clicked.connect(self.__calculate)
        self.ui.toolButtonExport.clicked.connect(self.__export_meal_episodes)

        self.meal_details_box_selector = MealDetailsBoxSelector(self.__filter_boxes)
        self.meal_details_box_selector.set_data(meal_details.dataset)
        self.ui.toolBox.addItem(self.meal_details_box_selector, QIcon(":/icons/icons8-dog-tag-16.png"), "Boxes")

        try:
            meal_details_settings = settings.value("MealDetailsSettings", MealDetailsSettings.get_default())
        except Exception:
            meal_details_settings = MealDetailsSettings.get_default()

        self.meal_details_settings_widget = MealDetailsSettingsWidget()
        self.meal_details_settings_widget.set_settings(meal_details_settings)
        self.meal_details_settings_widget.set_data(self.meal_details.dataset)
        self.ui.toolBox.addItem(self.meal_details_settings_widget, QIcon(":/icons/icons8-dog-tag-16.png"), "Settings")

        self.ui.splitter.setStretchFactor(0, 70)
        self.ui.splitter.setStretchFactor(1, 30)

        self.selected_boxes: list[MealDetailsBox] = []

        self.meal_events_df: pd.DataFrame | None = self.meal_details.raw_df
        self.meal_episodes_df: pd.DataFrame | None = None

    def __filter_boxes(self, selected_boxes: list[MealDetailsBox]):
        self.selected_boxes = selected_boxes
        self.__filter()

    def __filter(self):
        events_df = self.meal_events_df
        episodes_df = self.meal_episodes_df

        if len(self.selected_boxes) > 0:
            box_numbers = [b.box for b in self.selected_boxes]
            events_df = events_df[events_df["Box"].isin(box_numbers)]

            if episodes_df is not None:
                episodes_df = episodes_df[episodes_df["Box"].isin(box_numbers)]

        self.meal_events_table_view.set_data(events_df)
        self.meal_details_plot_widget.set_data(events_df)

        if episodes_df is not None:
            self.meal_episodes_table_view.set_data(episodes_df)

    def __calculate(self):
        tic = timeit.default_timer()

        meal_details_settings = self.meal_details_settings_widget.get_meal_details_settings()

        self.meal_events_df, self.meal_episodes_df = process_meal_details(self.meal_details, meal_details_settings)

        self.meal_events_table_view.set_data(self.meal_events_df)
        self.meal_episodes_table_view.set_data(self.meal_episodes_df)

        variables_subset: dict[str, Variable] = {}
        if "Drink1" in self.meal_details.variables:
            variables_subset["Drink1"] = self.meal_details.variables["Drink1"]
        if "Feed1" in self.meal_details.variables:
            variables_subset["Feed1"] = self.meal_details.variables["Feed1"]
        if "Drink2" in self.meal_details.variables:
            variables_subset["Drink2"] = self.meal_details.variables["Drink2"]
        if "Feed2" in self.meal_details.variables:
            variables_subset["Feed2"] = self.meal_details.variables["Feed2"]

        self.meal_episodes_offset_plot_widget.set_data(self.meal_episodes_df, variables_subset)
        self.meal_episodes_gap_plot_widget.set_data(self.meal_episodes_df, variables_subset)
        self.meal_episodes_intake_plot_widget.set_data(self.meal_episodes_df, variables_subset)

        self.ui.toolButtonExport.setEnabled(True)

        logger.info(f"Meal analysis complete: {timeit.default_timer() - tic} sec")
        Toast(text="Meal analysis complete.", parent=self, duration=4000).show_toast()

    def __export_meal_episodes(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export to CSV", "MealEpisodes", "CSV Files (*.csv)"
        )
        if filename:
            self.meal_episodes_df.to_csv(filename, sep=";", index=False)

    def hideEvent(self, event: QCloseEvent) -> None:
        settings = QSettings()
        settings.setValue("MealDetailsDialog/Geometry", self.saveGeometry())

        meal_details_settings = self.meal_details_settings_widget.get_meal_details_settings()
        settings.setValue("MealDetailsSettings", meal_details_settings)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Escape:
            return
        super().keyPressEvent(event)
