from typing import Optional

import pingouin as pg
import seaborn as sns
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QToolBar, QLabel, QComboBox

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

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self._get_toolbar())

        description_widget = QTextEdit(
            "The output of the Tukey test shows the average difference, a confidence interval as well as whether you should reject the null hypothesis for each pair of groups at the given significance level. In this case, the test suggests we reject the null hypothesis for 3 pairs, with each pair including the ""white"" category. This suggests the white group is likely different from the others. The 95% confidence interval plot reinforces the results visually: only 1 other group's confidence interval overlaps the white group's confidence interval.")
        description_widget.setFixedHeight(100)
        description_widget.setReadOnly(True)
        self.layout.addWidget(description_widget)

        self.webView = QWebEngineView(self)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PluginsEnabled, False)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PdfViewerEnabled, False)
        self.webView.setHtml('')
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

    def _analyze(self):
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

    def _get_toolbar(self) -> QToolBar:
        toolbar = QToolBar()
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        toolbar.addWidget(QLabel("Covariate: "))
        self.covariate_combo_box.currentTextChanged.connect(self._covariate_changed)
        toolbar.addWidget(self.covariate_combo_box)

        toolbar.addWidget(QLabel("Response: "))
        self.response_combo_box.currentTextChanged.connect(self._response_changed)
        toolbar.addWidget(self.response_combo_box)

        pushButtonAnalyze = QPushButton("Analyze")
        pushButtonAnalyze.clicked.connect(self._analyze)
        toolbar.addWidget(pushButtonAnalyze)

        return toolbar
