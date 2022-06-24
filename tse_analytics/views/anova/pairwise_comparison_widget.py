from typing import Optional

import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit

from tse_analytics.core.manager import Manager


class PairwiseComparisonWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        description_widget = QTextEdit(
            "The output of the Tukey test shows the average difference, a confidence interval as well as whether you should reject the null hypothesis for each pair of groups at the given significance level. In this case, the test suggests we reject the null hypothesis for 3 pairs, with each pair including the ""white"" category. This suggests the white group is likely different from the others. The 95% confidence interval plot reinforces the results visually: only 1 other group's confidence interval overlaps the white group's confidence interval.")
        description_widget.setFixedHeight(100)
        description_widget.setReadOnly(True)
        self.layout.addWidget(description_widget)

        self.webView = QWebEngineView(self)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PluginsEnabled, True)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PdfViewerEnabled, True)
        self.layout.addWidget(self.webView)

        self.canvas = FigureCanvas(Figure(figsize=(5.0, 4.0), dpi=100))
        self.ax = self.canvas.figure.subplots()

        # self.toolbar = NavigationToolbar(self.canvas, self)
        # self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)

    def analyze(self, df: pd.DataFrame, variable: str):
        if len(Manager.data.selected_groups) == 0:
            return

        # pt = pg.pairwise_tukey(dv=variable, between='Group', data=df)
        # self.webView.setHtml(pt.to_html())

        tukey = pairwise_tukeyhsd(endog=df[variable],  # Data
                                  groups=df["Group"],  # Groups
                                  alpha=0.05)  # Significance level

        self.webView.setHtml(tukey.summary().as_html())

        self.ax.clear()
        tukey.plot_simultaneous(ax=self.ax, figsize=self.canvas.figure.get_size_inches())  # Plot group confidence intervals
        # self.ax.vlines(x=2.57, ymin=-0.5, ymax=4.5, color="red")
        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def clear(self):
        self.webView.setHtml("")
        self.ax.clear()
