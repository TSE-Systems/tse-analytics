import os.path
from typing import Optional

import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
import pingouin as pg
import seaborn as sns
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget, QComboBox, QToolBar, QLabel, QPushButton

from tse_analytics.core.manager import Manager
from tse_analytics.css import style
from tse_analytics.views.analysis.analysis_widget import AnalysisWidget
from tse_datatools.data.variable import Variable

pd.set_option('colheader_justify', 'center')  # FOR TABLE <th>
sns.set_theme(style="whitegrid")


class CorrelationWidget(AnalysisWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.x_combo_box = QComboBox(self)
        self.x = ""

        self.y_combo_box = QComboBox(self)
        self.y = ""

        self.layout.addWidget(self._get_toolbar())

        self.webView = QWebEngineView(self)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PluginsEnabled, False)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PdfViewerEnabled, False)
        self.webView.setHtml('')
        self.layout.addWidget(self.webView)

        self.figure = None
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.layout.addWidget(self.canvas)

    def update_variables(self, variables: dict[str, Variable]):
        self.x = ""
        self.y = ""

        self.x_combo_box.clear()
        self.x_combo_box.addItems(variables)
        self.x_combo_box.setCurrentText("")

        self.y_combo_box.clear()
        self.y_combo_box.addItems(variables)
        self.y_combo_box.setCurrentText("")

    def _analyze(self):
        if len(Manager.data.selected_dataset.groups) == 0:
            return

        df = Manager.data.selected_dataset.original_df

        multivariate_normality = pg.multivariate_normality(df[[self.x, self.y]])
        corr = pg.pairwise_corr(data=df, columns=[self.x, self.y], method='pearson')

        html_template = '''
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
                '''

        html = html_template.format(
            style=style,
            multivariate_normality=multivariate_normality,
            corr=corr.to_html(classes='mystyle'),
        )
        self.webView.setHtml(html)

        g = sns.jointplot(data=df, x=self.x, y=self.y, hue="Group")
        self.figure = g.figure
        self.canvas.figure = self.figure
        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def clear(self):
        self.x_combo_box.clear()
        self.y_combo_box.clear()
        self.webView.setHtml("")

    def _x_current_text_changed(self, x: str):
        self.x = x

    def _y_current_text_changed(self, y: str):
        self.y = y

    @property
    def help_content(self) -> Optional[str]:
        path = 'docs/correlation.md'
        if os.path.exists(path):
            with open(path, 'r') as file:
                return file.read().rstrip()

    def _get_toolbar(self) -> QToolBar:
        toolbar = super()._get_toolbar()

        toolbar.addWidget(QLabel("X: "))
        self.x_combo_box.currentTextChanged.connect(self._x_current_text_changed)
        toolbar.addWidget(self.x_combo_box)

        toolbar.addWidget(QLabel("Y: "))
        self.y_combo_box.currentTextChanged.connect(self._y_current_text_changed)
        toolbar.addWidget(self.y_combo_box)

        pushButtonAnalyze = QPushButton("Analyze")
        pushButtonAnalyze.clicked.connect(self._analyze)
        toolbar.addWidget(pushButtonAnalyze)

        return toolbar
