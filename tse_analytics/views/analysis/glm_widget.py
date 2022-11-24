from typing import Optional

import pingouin as pg
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QToolBar, QLabel, QComboBox

from tse_analytics.core.manager import Manager
from tse_analytics.css import style
from tse_datatools.data.variable import Variable


class GlmWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.covariate_combo_box = QComboBox(self)
        self.covariate = ""

        self.response_combo_box = QComboBox(self)
        self.response = ""

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self._get_toolbar())

        description_widget = QTextEdit(
            "The output of the Tukey test shows the average difference, a confidence interval as well as whether you should reject the null hypothesis for each pair of groups at the given significance level. In this case, the test suggests we reject the null hypothesis for 3 pairs, with each pair including the ""white"" category. This suggests the white group is likely different from the others. The 95% confidence interval plot reinforces the results visually: only 1 other group's confidence interval overlaps the white group's confidence interval.")
        description_widget.setFixedHeight(100)
        description_widget.setReadOnly(True)
        self.layout.addWidget(description_widget)

        self.webView = QWebEngineView(self)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PluginsEnabled, True)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PdfViewerEnabled, True)
        self.layout.addWidget(self.webView)

        figure = Figure(figsize=(5.0, 4.0), dpi=100)
        self.ax = figure.subplots()
        self.canvas = FigureCanvasQTAgg(figure)
        self.layout.addWidget(self.canvas)

    def clear(self):
        self.webView.setHtml("")
        self.ax.clear()

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
        df = Manager.data.selected_dataset.original_df

        glm = pg.linear_regression(df[[self.covariate]], df[self.response])

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
