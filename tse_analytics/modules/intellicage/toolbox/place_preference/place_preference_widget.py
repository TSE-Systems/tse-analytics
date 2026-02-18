import pandas as pd
from pyqttoast import ToastPreset
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFileDialog, QInputDialog, QToolBar, QVBoxLayout, QWidget

from tse_analytics.core import manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.report import Report
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_figsize_from_widget, get_h_spacer_widget, get_widget_tool_button
from tse_analytics.core.workers import TaskManager, Worker
from tse_analytics.modules.intellicage.toolbox.place_preference.place_preference_settings_widget_ui import (
    Ui_PlacePreferencesSettingsWidget,
)
from tse_analytics.modules.intellicage.toolbox.place_preference.processor import (
    IntelliCagePlacePreferenceResult,
    get_intellicage_place_preference_result,
)
from tse_analytics.toolbox.toolbox_registry import toolbox_plugin
from tse_analytics.views.misc.report_edit import ReportEdit


@toolbox_plugin(category="IntelliCage", label="Place Preference", icon=":/icons/icons8-corner-16.png", order=1)
class PlacePreferenceWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Place Preference"

        self.datatable = datatable

        self.visit_counts: pd.DataFrame | None = None
        self.normalized_visit_counts: pd.DataFrame | None = None
        self.visit_results: pd.DataFrame | None = None
        self.duration_results: pd.DataFrame | None = None

        # Setup toolbar
        toolbar = QToolBar(
            "Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

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

        # Insert the toolbar to the widget
        self._layout.addWidget(toolbar)

        self.report_view = ReportEdit(self)
        self._layout.addWidget(self.report_view)

        toolbar.addWidget(get_h_spacer_widget(toolbar))

        self.export_excel_action = toolbar.addAction(QIcon(":/icons/icons8-export-16.png"), "Export to Excel")
        self.export_excel_action.triggered.connect(self._export_to_excel)
        self.export_excel_action.setEnabled(False)

        toolbar.addAction("Add Report").triggered.connect(self._add_report)

    def _update(self) -> None:
        self.report_view.clear()

        self.visit_counts = None
        self.normalized_visit_counts = None
        self.visit_results = None
        self.duration_results = None

        columns = ["Animal", "Corner", "VisitDuration", "CornerCondition", "NosepokesNumber", "LicksNumber"]
        df = self.datatable.get_filtered_df(columns)

        if self.settings_widget_ui.checkBoxVisitsWithNosepokes.isChecked():
            df = df[df["NosepokesNumber"] > 0]
        if self.settings_widget_ui.checkBoxVisitsWithLicks.isChecked():
            df = df[df["LicksNumber"] > 0]

        if not self.settings_widget_ui.radioButtonNone.isChecked():
            if self.settings_widget_ui.checkBoxNeutral.isChecked():
                df.loc[df["CornerCondition"] == "Neutral", "CornerCondition"] = "Correct"
            if self.settings_widget_ui.checkBoxIncorrect.isChecked():
                df.loc[df["CornerCondition"] == "Incorrect", "CornerCondition"] = "Correct"

            if self.settings_widget_ui.radioButtonCorrect.isChecked():
                # Exclude correct visits
                df = df[df["CornerCondition"] != "Correct"]
            if self.settings_widget_ui.radioButtonIncorrect.isChecked():
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

        self._toast = make_toast(self, self.title, "Processing...")
        self._toast.show()

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
        self._toast.hide()
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

    def _add_report(self):
        name, ok = QInputDialog.getText(
            self,
            "Report",
            "Please enter report name:",
            text=self.title,
        )
        if ok and name:
            manager.add_report(
                Report(
                    self.datatable.dataset,
                    name,
                    self.report_view.toHtml(),
                )
            )
