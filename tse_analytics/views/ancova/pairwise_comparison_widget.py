from typing import Optional

import pandas as pd
import pingouin as pg
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit

from tse_analytics.core.manager import Manager


class PairwiseComparisonWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        description_widget = QTextEdit(
            "An ANCOVA (“analysis of covariance”) is used to determine whether or not there is a statistically significant difference between the means of three or more independent groups, after controlling for one or more covariates. The additional continuous independent variable in ANCOVA is called a covariate (also known as control, concomitant, or confounding variable).")
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

    def analyze(self, df: pd.DataFrame, covariate: str, response: str):
        if len(Manager.data.selected_groups) == 0:
            return

        result = pg.ancova(data=df, dv=response, covar=covariate, between="Group")

        self.webView.setHtml(result.to_html())

    def clear(self):
        self.webView.setHtml("")
        self.ax.clear()
