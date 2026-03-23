from dataclasses import dataclass
from enum import Enum

import pandas as pd
from pyqttoast import ToastPreset
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFileDialog, QToolBar, QWidget

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_figsize_from_widget, get_widget_tool_button
from tse_analytics.core.workers import TaskManager, Worker
from tse_analytics.modules.intellicage.toolbox.place_preference.place_preference_settings_widget_ui import (
    Ui_PlacePreferencesSettingsWidget,
)
from tse_analytics.modules.intellicage.toolbox.place_preference.processor import (
    IntelliCagePlacePreferenceResult,
    get_intellicage_place_preference_result,
)
from tse_analytics.toolbox.toolbox_registry import toolbox_plugin
from tse_analytics.toolbox.toolbox_widget_base import ToolboxWidgetBase


class ExcludeConditionMode(Enum):
    EXCLUDE_NONE = 0
    EXCLUDE_CORRECT = 1
    EXCLUDE_INCORRECT = 2


@dataclass
class PlacePreferenceWidgetSettings:
    correct_place: bool = True
    neutral_place: bool = False
    incorrect_place: bool = False
    exclude_condition: ExcludeConditionMode = ExcludeConditionMode.EXCLUDE_NONE
    only_visits_with_nosepokes: bool = False
    only_visits_with_licks: bool = False


@toolbox_plugin(category="IntelliCage", label="Place Preference", icon=":/icons/icons8-corner-16.png", order=1)
class PlacePreferenceWidget(ToolboxWidgetBase):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(
            datatable,
            PlacePreferenceWidgetSettings,
            "Place Preference",
            parent,
        )

        self.visit_counts: pd.DataFrame | None = None
        self.normalized_visit_counts: pd.DataFrame | None = None
        self.visit_results: pd.DataFrame | None = None
        self.duration_results: pd.DataFrame | None = None

    def _create_toolbar_items(self, toolbar: QToolBar) -> None:
        self.update_action = toolbar.addAction(QIcon(":/icons/icons8-refresh-16.png"), "Update")
        self.update_action.triggered.connect(self._update)

        self.settings_widget = QWidget()
        self.settings_widget_ui = Ui_PlacePreferencesSettingsWidget()
        self.settings_widget_ui.setupUi(self.settings_widget)
        settings_button = get_widget_tool_button(
            toolbar,
            self.settings_widget,
            "Settings",
            QIcon(":/icons/icons8-settings-16.png"),
        )
        toolbar.addWidget(settings_button)

        self.export_excel_action = toolbar.addAction(QIcon(":/icons/icons8-export-16.png"), "Export to Excel")
        self.export_excel_action.triggered.connect(self._export_to_excel)
        self.export_excel_action.setEnabled(False)

    def _get_settings_value(self):
        exclude_condition = ExcludeConditionMode.EXCLUDE_NONE
        if self.settings_widget_ui.radioButtonCorrect.isChecked():
            exclude_condition = ExcludeConditionMode.EXCLUDE_CORRECT
        elif self.settings_widget_ui.radioButtonIncorrect.isChecked():
            exclude_condition = ExcludeConditionMode.EXCLUDE_INCORRECT

        return PlacePreferenceWidgetSettings(
            self.settings_widget_ui.checkBoxCorrect.isChecked(),
            self.settings_widget_ui.checkBoxNeutral.isChecked(),
            self.settings_widget_ui.checkBoxIncorrect.isChecked(),
            exclude_condition,
            self.settings_widget_ui.checkBoxVisitsWithNosepokes.isChecked(),
            self.settings_widget_ui.checkBoxVisitsWithLicks.isChecked(),
        )

    def _update(self) -> None:
        self.report_view.clear()

        self.visit_counts = None
        self.normalized_visit_counts = None
        self.visit_results = None
        self.duration_results = None

        columns = ["Animal", "Corner", "VisitDuration", "CornerCondition", "NosepokesNumber", "LicksNumber"]
        df = self.datatable.get_filtered_df(columns)

        settings = self._get_settings_value()

        if settings.only_visits_with_nosepokes:
            df = df[df["NosepokesNumber"] > 0]
        if settings.only_visits_with_licks:
            df = df[df["LicksNumber"] > 0]

        if settings.exclude_condition != ExcludeConditionMode.EXCLUDE_NONE:
            if settings.neutral_place:
                df.loc[df["CornerCondition"] == "Neutral", "CornerCondition"] = "Correct"
            if settings.incorrect_place:
                df.loc[df["CornerCondition"] == "Incorrect", "CornerCondition"] = "Correct"

            if settings.exclude_condition == ExcludeConditionMode.EXCLUDE_CORRECT:
                # Exclude correct visits
                df = df[df["CornerCondition"] != "Correct"]
            if settings.exclude_condition == ExcludeConditionMode.EXCLUDE_INCORRECT:
                # Exclude incorrect visits
                df = df[df["CornerCondition"] != "Incorrect"]

        if df.empty:
            make_toast(
                self,
                self.title,
                "No visits to analyze. Please adjust the settings and try again.",
                duration=2000,
                preset=ToastPreset.WARNING,
            ).show()
            return

        self.update_action.setEnabled(False)
        self.export_excel_action.setEnabled(False)

        self.toast = make_toast(self, self.title, "Processing...")
        self.toast.show()

        worker = Worker(
            get_intellicage_place_preference_result,
            self.datatable.dataset,
            df,
            get_figsize_from_widget(self.report_view),
        )
        worker.signals.result.connect(self._result)
        worker.signals.finished.connect(self._finished)
        TaskManager.start_task(worker)

    def _result(self, result: IntelliCagePlacePreferenceResult):
        self.report_view.set_content(result.report)

        self.visit_counts = result.visit_counts
        self.normalized_visit_counts = result.normalized_visit_counts
        self.visit_results = result.visit_results
        self.duration_results = result.duration_results

    def _finished(self):
        self.toast.hide()
        self.update_action.setEnabled(True)
        self.export_excel_action.setEnabled(True)

    def _export_to_excel(self) -> None:
        if self.datatable is None or self.visit_counts is None:
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Export to Excel", "", "Excel Files (*.xlsx)")
        if filename:
            with pd.ExcelWriter(filename) as writer:
                self.visit_counts.to_excel(writer, sheet_name="Visit Counts")
                self.normalized_visit_counts.to_excel(writer, sheet_name="Normalized Visit Counts")
                self.visit_results.to_excel(writer, sheet_name="Visit Results")
                self.duration_results.to_excel(writer, sheet_name="Visit Duration Results")
