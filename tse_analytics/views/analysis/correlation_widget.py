import os.path
from typing import Optional

import pandas as pd
import pingouin as pg
import seaborn as sns
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QLabel, QPushButton, QToolBar, QWidget

from tse_analytics.core.manager import Manager
from tse_analytics.css import style
from tse_analytics.views.analysis.analysis_widget import AnalysisWidget
from tse_analytics.views.misc.variable_selector import VariableSelector
from tse_datatools.data.variable import Variable

pd.set_option("colheader_justify", "center")  # FOR TABLE <th>
sns.set_theme(style="whitegrid")


class CorrelationWidget(AnalysisWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.x_combo_box = VariableSelector()
        self.x_combo_box.currentTextChanged.connect(self._x_current_text_changed)
        self.x_var = ""

        self.y_combo_box = VariableSelector()
        self.y_combo_box.currentTextChanged.connect(self._y_current_text_changed)
        self.y_var = ""

        self.layout().addWidget(self._get_toolbar())

        self.webView = QWebEngineView(self)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PluginsEnabled, False)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PdfViewerEnabled, False)
        self.webView.setHtml("")
        self.layout().addWidget(self.webView)

        self.figure = None
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.layout().addWidget(self.canvas)

    def update_variables(self, variables: dict[str, Variable]):
        self.x_combo_box.set_data(variables)
        self.y_combo_box.set_data(variables)

    def __analyze(self):
        if len(Manager.data.selected_dataset.groups) == 0:
            return

        df = Manager.data.selected_dataset.original_df

        multivariate_normality = pg.multivariate_normality(df[[self.x_var, self.y_var]])
        corr = pg.pairwise_corr(data=df, columns=[self.x_var, self.y_var], method="pearson")

        html_template = """
                <html>
                  <head>
                    <title>HTML Pandas Dataframe with CSS</title>
                    {style}
                  </head>
                  <body>
                    <h3>Test for bivariate normality (Henze-Zirkler)</h3>
                    {multivariate_normality}
                    <h3>Pearson correlation</h3>
                    {corr}
                  </body>
                </html>
                """

        html = html_template.format(
            style=style,
            multivariate_normality=multivariate_normality,
            corr=corr.to_html(classes="mystyle"),
        )
        self.webView.setHtml(html)

        g = sns.jointplot(data=df, x=self.x_var, y=self.y_var, hue="Group")
        self.figure = g.figure
        self.canvas.figure = self.figure
        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def clear(self):
        self.x_combo_box.clear()
        self.y_combo_box.clear()
        self.webView.setHtml("")

    def _x_current_text_changed(self, x: str):
        self.x_var = x

    def _y_current_text_changed(self, y: str):
        self.y_var = y

    @property
    def help_content(self) -> Optional[str]:
        path = "docs/correlation.md"
        if os.path.exists(path):
            with open(path, "r") as file:
                return file.read().rstrip()
        return None

    def _get_toolbar(self) -> QToolBar:
        toolbar = super()._get_toolbar()

        toolbar.addWidget(QLabel("X: "))
        toolbar.addWidget(self.x_combo_box)

        toolbar.addWidget(QLabel("Y: "))
        toolbar.addWidget(self.y_combo_box)

        button = QPushButton("Analyze")
        button.clicked.connect(self.__analyze)
        toolbar.addWidget(button)

        return toolbar
