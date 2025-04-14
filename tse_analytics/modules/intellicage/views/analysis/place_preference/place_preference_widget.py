import pandas as pd
import seaborn as sns
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar, QFileDialog
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from scipy.stats import chisquare, kruskal

from tse_analytics.core import messaging
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.utils import get_html_image, get_h_spacer_widget
from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.pdf.pdf_widget import PdfWidget


class PlacePreferenceWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Place Preference"

        self.datatable = datatable

        self.visit_results: pd.DataFrame | None = None
        self.visit_counts: pd.DataFrame | None = None
        self.normalized_visit_counts: pd.DataFrame | None = None
        self.duration_results: pd.DataFrame | None = None

        # Setup toolbar
        toolbar = QToolBar(
            "Place Preference Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        toolbar.addAction(QIcon(":/icons/icons8-refresh-16.png"), "Update").triggered.connect(self._update)
        toolbar.addSeparator()

        self.export_excel_action = toolbar.addAction(QIcon(":/icons/icons8-export-16.png"), "Export to Excel")
        self.export_excel_action.triggered.connect(self._export_to_excel)
        self.export_excel_action.setEnabled(False)

        # Insert toolbar to the widget
        self.layout.addWidget(toolbar)

        self.canvas = MplCanvas(self)
        self.layout.addWidget(self.canvas)

        plot_toolbar = NavigationToolbar2QT(self.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        toolbar.addWidget(plot_toolbar)

        toolbar.addWidget(get_h_spacer_widget(toolbar))
        toolbar.addAction("Add to Report").triggered.connect(self._add_report)

        self.pdf_widget: PdfWidget | None = None

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

    def _update(self):
        columns = ["Animal", "Corner", "VisitDuration"]
        df = self.datatable.get_filtered_df(columns)

        self.canvas.clear(False)
        axs = self.canvas.figure.subplots(1, 2, sharey=False)

        self.visit_results, self.visit_counts = self._analyze_visits(df)
        self.duration_results = self._analyze_durations(df)

        sns.heatmap(
            self.visit_counts,
            annot=True,
            cmap="YlGnBu",
            fmt="d",
            ax=axs[0],
        )
        axs[0].set(
            title="Visit Counts per Corner",
        )

        self.normalized_visit_counts = self.visit_counts.div(
            self.visit_counts.sum(axis=1),
            axis=0,
        )
        self.normalized_visit_counts.plot(
            kind="barh",
            stacked=True,
            ax=axs[1],
            # sharey=True,
        )
        axs[1].invert_yaxis()
        axs[1].set(
            title="Proportional Visit Distribution",
        )

        # sns.boxplot(x='Corner', y='VisitDuration', data=df, ax=axs[1])
        # axs[1].set(
        #     title="Visit Durations by Corner",
        #     xlabel="Corner",
        #     ylabel="Duration (s)",
        # )

        self.canvas.figure.tight_layout()
        self.canvas.draw()

        self.export_excel_action.setEnabled(True)

    def _export_to_excel(self):
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
        self.datatable.dataset.report += get_html_image(self.canvas.figure)
        messaging.broadcast(messaging.AddToReportMessage(self, self.datatable.dataset))
