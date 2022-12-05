from typing import Optional
import os.path

import pingouin as pg
import seaborn as sns
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget, QPushButton, QToolBar, QLabel, QComboBox

from tse_analytics.core.manager import Manager
from tse_analytics.css import style
from tse_analytics.views.analysis.analysis_widget import AnalysisWidget
from tse_datatools.data.variable import Variable


class GlmWidget(AnalysisWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.covariate_combo_box = QComboBox(self)
        self.covariate = ''

        self.response_combo_box = QComboBox(self)
        self.response = ''

        self.layout.addWidget(self._get_toolbar())

        self.webView = QWebEngineView(self)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PluginsEnabled, True)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PdfViewerEnabled, True)
        self.layout.addWidget(self.webView)

        self.canvas = None

    def clear(self):
        self.webView.setHtml('')

    def update_variables(self, variables: dict[str, Variable]):
        self.covariate = ''
        self.response = ''

        self.covariate_combo_box.clear()
        self.covariate_combo_box.addItems(variables)
        self.covariate_combo_box.setCurrentText(self.covariate)

        self.response_combo_box.clear()
        self.response_combo_box.addItems(variables)
        self.response_combo_box.setCurrentText(self.response)

    def _covariate_changed(self, covariate: str):
        self.covariate = covariate

    def _response_changed(self, response: str):
        self.response = response

    def __analyze(self):
        df = Manager.data.selected_dataset.original_df.copy()
        # cols = df.columns
        df = df.groupby(by=['Animal'], as_index=False).agg({self.response: 'mean', 'Group': 'first'})
        # df = df.reset_index()

        df['Weight'] = df['Animal'].astype(float)
        weights = {}
        for animal in Manager.data.selected_dataset.animals.values():
            weights[animal.id] = animal.weight
        df = df.replace({'Weight': weights})

        if self.canvas is not None:
            self.layout.removeWidget(self.canvas)

        facet_grid = sns.lmplot(x='Weight', y=self.response, hue="Group", robust=False, data=df)
        self.canvas = FigureCanvasQTAgg(facet_grid.figure)
        self.canvas.updateGeometry()
        self.canvas.draw()
        self.layout.addWidget(self.canvas)

        glm = pg.linear_regression(df[['Weight']], df[self.response])

        html_template = '''
                <html>
                  <head>
                    {style}
                  </head>
                  <body>
                    <h3>GLM</h3>
                    {glm}
                  </body>
                </html>
                '''

        html = html_template.format(
            style=style,
            glm=glm.to_html(classes='mystyle'),
        )
        self.webView.setHtml(html)

    @property
    def help_content(self) -> Optional[str]:
        path = 'docs/glm.md'
        if os.path.exists(path):
            with open(path, 'r') as file:
                return file.read().rstrip()

    def _get_toolbar(self) -> QToolBar:
        toolbar = super()._get_toolbar()

        toolbar.addWidget(QLabel("Covariate: "))
        self.covariate_combo_box.currentTextChanged.connect(self._covariate_changed)
        toolbar.addWidget(self.covariate_combo_box)

        toolbar.addWidget(QLabel("Response: "))
        self.response_combo_box.currentTextChanged.connect(self._response_changed)
        toolbar.addWidget(self.response_combo_box)

        pushButtonAnalyze = QPushButton("Analyze")
        pushButtonAnalyze.clicked.connect(self.__analyze)
        toolbar.addWidget(pushButtonAnalyze)

        return toolbar
