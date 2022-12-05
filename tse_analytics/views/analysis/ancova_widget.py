import os.path
from typing import Optional

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
import pingouin as pg
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget, QComboBox, QToolBar, QLabel, QPushButton
from matplotlib.figure import Figure

from tse_analytics.core.manager import Manager
from tse_analytics.css import style
from tse_analytics.views.analysis.analysis_widget import AnalysisWidget
from tse_datatools.data.variable import Variable


class AncovaWidget(AnalysisWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.covariate_combo_box = QComboBox(self)
        self.covariate = ""

        self.response_combo_box = QComboBox(self)
        self.response = ""

        self.layout.addWidget(self._get_toolbar())

        self.webView = QWebEngineView(self)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PluginsEnabled, True)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PdfViewerEnabled, True)
        self.layout.addWidget(self.webView)

        figure = Figure(figsize=(5.0, 4.0), dpi=100)
        self.ax = figure.subplots()
        self.canvas = FigureCanvasQTAgg(figure)
        self.layout.addWidget(self.canvas)

    def update_variables(self, variables: dict[str, Variable]):
        self.covariate = ''
        self.response = ''

        self.covariate_combo_box.clear()
        self.covariate_combo_box.addItems(variables)
        self.covariate_combo_box.setCurrentText(self.covariate)

        self.response_combo_box.clear()
        self.response_combo_box.addItems(variables)
        self.response_combo_box.setCurrentText(self.response)

    def __analyze(self):
        df = Manager.data.selected_dataset.original_df

        ancova = pg.ancova(data=df, dv=self.response, covar=self.covariate, between="Group")

        html_template = '''
                <html>
                  <head>
                    {style}
                  </head>
                  <body>
                    <h3>ANCOVA</h3>
                    {ancova}
                  </body>
                </html>
                '''

        html = html_template.format(
            style=style,
            ancova=ancova.to_html(classes='mystyle'),
        )
        self.webView.setHtml(html)

    def clear(self):
        self.covariate_combo_box.clear()
        self.response_combo_box.clear()
        self.webView.setHtml('')
        self.ax.clear()

    def _covariate_current_text_changed(self, covariate: str):
        self.covariate = covariate

    def _response_current_text_changed(self, response: str):
        self.response = response

    @property
    def help_content(self) -> Optional[str]:
        path = 'docs/ancova.md'
        if os.path.exists(path):
            with open(path, 'r') as file:
                return file.read().rstrip()

    def _get_toolbar(self) -> QToolBar:
        toolbar = super()._get_toolbar()

        toolbar.addWidget(QLabel("Covariate: "))
        self.covariate_combo_box.currentTextChanged.connect(self._covariate_current_text_changed)
        toolbar.addWidget(self.covariate_combo_box)

        toolbar.addWidget(QLabel("Response: "))
        self.response_combo_box.currentTextChanged.connect(self._response_current_text_changed)
        toolbar.addWidget(self.response_combo_box)

        pushButtonAnalyze = QPushButton("Analyze")
        pushButtonAnalyze.clicked.connect(self.__analyze)
        toolbar.addWidget(pushButtonAnalyze)

        return toolbar
