import pandas as pd
import seaborn as sns
from pyqttoast import ToastPreset
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFileDialog, QTabWidget, QToolBar, QVBoxLayout, QWidget
from scipy.stats import chisquare, kruskal

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_widget_tool_button
from tse_analytics.modules.intellicage.toolbox.place_preference.place_preference_settings_widget_ui import (
    Ui_PlacePreferencesSettingsWidget,
)
from tse_analytics.views.misc.pandas_widget import PandasWidget
from tse_analytics.views.misc.plot_widget import PlotWidget


class PlacePreferenceWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Place Preference"

        self.datatable = datatable

        self.visit_results: pd.DataFrame | None = None
        self.visit_counts: pd.DataFrame | None = None
        self.normalized_visit_counts: pd.DataFrame | None = None
        self.duration_results: pd.DataFrame | None = None

        # Setup toolbar
        toolbar = QToolBar(
            "Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        toolbar.addAction(QIcon(":/icons/icons8-refresh-16.png"), "Update").triggered.connect(self._update)

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

        toolbar.addSeparator()

        self.export_excel_action = toolbar.addAction(QIcon(":/icons/icons8-export-16.png"), "Export to Excel")
        self.export_excel_action.triggered.connect(self._export_to_excel)
        self.export_excel_action.setEnabled(False)

        # Insert the toolbar to the widget
        self._layout.addWidget(toolbar)

        self.tab_widget = QTabWidget()
        self._layout.addWidget(self.tab_widget)

        self.visit_counts_plot_widget = PlotWidget(self.datatable)
        self.tab_widget.addTab(self.visit_counts_plot_widget, "Visit Counts")

        self.visit_duration_plot_widget = PlotWidget(self.datatable)
        self.tab_widget.addTab(self.visit_duration_plot_widget, "Visit Duration")

        self.visit_results_pandas_widget = PandasWidget(self.datatable.dataset, "Visit Results")
        self.tab_widget.addTab(self.visit_results_pandas_widget, "Visit Results")

        self.duration_results_pandas_widget = PandasWidget(self.datatable.dataset, "Duration Results")
        self.tab_widget.addTab(self.duration_results_pandas_widget, "Duration Results")

    def _analyze_visits(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Analyze visit counts using chi-square goodness-of-fit test"""
        visit_counts = df.groupby(["Animal", "Corner"], observed=True).size().unstack(fill_value=0)
        visit_counts.sort_values(by=["Animal"], inplace=True)

        results = []
        for animal in visit_counts.index:
            observed = visit_counts.loc[animal].values
            total = observed.sum()
            expected = [total / len(observed)] * len(observed)
            chi2, p = chisquare(observed, expected)

            results.append({"Animal": animal, "chi2": chi2, "p_value": p, "significant": p < 0.05})

        return pd.DataFrame(results), visit_counts

    def _analyze_durations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze duration distributions using Kruskal-Wallis test"""
        results = []
        for animal in df["Animal"].unique():
            animal_data = df[df["Animal"] == animal]
            corners = animal_data["Corner"].unique()

            if len(corners) < 2:
                continue  # Skip mice with only one corner visited

            groups = [animal_data[animal_data["Corner"] == corner]["VisitDuration"].values for corner in corners]
            h_stat, p_value = kruskal(*groups)

            results.append({
                "Animal": animal,
                "h_statistic": h_stat,
                "p_value": p_value,
                "significant": p_value < 0.05,
            })

        return pd.DataFrame(results)

    def _update(self) -> None:
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

        self.visit_counts_plot_widget.clear(False)
        self.visit_duration_plot_widget.clear(False)

        if df.empty:
            make_toast(
                self,
                self.title,
                "No visits to analyze. Please adjust the settings and try again.",
                duration=2000,
                preset=ToastPreset.WARNING,
            ).show()
            return

        visit_counts_axes = self.visit_counts_plot_widget.canvas.figure.subplots(1, 2, sharey=False)

        self.visit_results, self.visit_counts = self._analyze_visits(df)
        self.duration_results = self._analyze_durations(df)

        self.visit_results_pandas_widget.set_data(self.visit_results)
        self.duration_results_pandas_widget.set_data(self.duration_results)

        sns.heatmap(
            self.visit_counts,
            annot=True,
            cmap="YlGnBu",
            fmt="d",
            ax=visit_counts_axes[0],
        )
        visit_counts_axes[0].set(
            title="Visit Counts per Corner",
        )

        self.normalized_visit_counts = self.visit_counts.div(
            self.visit_counts.sum(axis=1),
            axis=0,
        )
        self.normalized_visit_counts.plot(
            kind="barh",
            stacked=True,
            ax=visit_counts_axes[1],
            # sharey=True,
        )
        visit_counts_axes[1].invert_yaxis()
        visit_counts_axes[1].set(
            title="Proportional Visit Distribution",
        )

        self.visit_counts_plot_widget.canvas.figure.tight_layout()
        self.visit_counts_plot_widget.canvas.draw()

        visit_duration_axes = self.visit_duration_plot_widget.canvas.figure.subplots(1, 1)
        sns.boxplot(x="Corner", y="VisitDuration", data=df, ax=visit_duration_axes)
        visit_duration_axes.set(
            title="Visit Durations by Corner",
            xlabel="Corner",
            ylabel="Duration (s)",
        )

        self.visit_duration_plot_widget.canvas.figure.tight_layout()
        self.visit_duration_plot_widget.canvas.draw()

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
