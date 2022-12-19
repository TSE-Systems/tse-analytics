from typing import Optional

import pingouin as pg
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QLabel, QWidget

from tse_analytics.core.manager import Manager
from tse_analytics.css import style
from tse_analytics.views.analysis.analysis_widget import AnalysisWidget
from tse_analytics.views.misc.variable_selector import VariableSelector
from tse_datatools.data.variable import Variable


class AncovaWidget(AnalysisWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.help_path = "docs/ancova.md"

        self.covariate = ""
        self.covariate_combo_box = VariableSelector()
        self.covariate_combo_box.currentTextChanged.connect(self._covariate_current_text_changed)
        self.toolbar.addWidget(QLabel("Covariate: "))
        self.toolbar.addWidget(self.covariate_combo_box)

        self.response = ""
        self.response_combo_box = VariableSelector()
        self.response_combo_box.currentTextChanged.connect(self._response_current_text_changed)
        self.toolbar.addWidget(QLabel("Response: "))
        self.toolbar.addWidget(self.response_combo_box)

        self.webView = QWebEngineView(self)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PluginsEnabled, False)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PdfViewerEnabled, False)
        self.webView.setHtml("")
        self.layout().addWidget(self.webView)

        figure = Figure(figsize=(5.0, 4.0), dpi=100)
        self.ax = figure.subplots()
        self.canvas = FigureCanvasQTAgg(figure)
        self.layout().addWidget(self.canvas)

    def update_variables(self, variables: dict[str, Variable]):
        self.covariate_combo_box.set_data(variables)
        self.response_combo_box.set_data(variables)

    def _analyze(self):
        df = Manager.data.selected_dataset.original_df

        ancova = pg.ancova(data=df, dv=self.response, covar=self.covariate, between="Group")

        html_template = """
                <html>
                  <head>
                    {style}
                  </head>
                  <body>
                    <h3>ANCOVA</h3>
                    {ancova}
                  </body>
                </html>
                """

        html = html_template.format(
            style=style,
            ancova=ancova.to_html(classes="mystyle"),
        )
        self.webView.setHtml(html)

    def clear(self):
        self.covariate_combo_box.clear()
        self.response_combo_box.clear()
        self.webView.setHtml("")
        self.ax.clear()

    def _covariate_current_text_changed(self, covariate: str):
        self.covariate = covariate

    def _response_current_text_changed(self, response: str):
        self.response = response
