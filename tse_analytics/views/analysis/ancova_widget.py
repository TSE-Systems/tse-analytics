from typing import Optional

import pingouin as pg
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QLabel, QWidget, QSplitter

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

        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.layout().addWidget(self.splitter)

        figure = Figure(figsize=(5.0, 4.0), dpi=100)
        self.ax = figure.subplots()
        self.canvas = FigureCanvasQTAgg(figure)
        self.splitter.addWidget(self.canvas)

        self.web_view = QWebEngineView(self)
        self.web_view.settings().setAttribute(self.web_view.settings().WebAttribute.PluginsEnabled, False)
        self.web_view.settings().setAttribute(self.web_view.settings().WebAttribute.PdfViewerEnabled, False)
        self.web_view.setHtml("")
        self.splitter.addWidget(self.web_view)

        self.splitter.setSizes([2, 1])

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
        self.web_view.setHtml(html)

    def clear(self):
        self.covariate_combo_box.clear()
        self.response_combo_box.clear()
        self.web_view.setHtml("")
        self.ax.clear()

    def _covariate_current_text_changed(self, covariate: str):
        self.covariate = covariate

    def _response_current_text_changed(self, response: str):
        self.response = response
