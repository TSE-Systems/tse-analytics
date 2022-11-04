from typing import Optional

import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pingouin as pg
import seaborn as sns
from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QComboBox, QToolBar, QLabel, QPushButton
from matplotlib.figure import Figure

from tse_analytics.core.manager import Manager
from tse_analytics.css import style


class AncovaWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.covariate_combo_box = QComboBox(self)
        self.covariate = ""

        self.response_combo_box = QComboBox(self)
        self.response = ""

        self.layout.addWidget(self.toolbar)

        description_widget = QTextEdit(
            "hz: The Henze-Zirkler test statistic <br/>pval: P-value <br/>normal: True if input comes from a multivariate normal distribution"
        )
        description_widget.setFixedHeight(100)
        description_widget.setReadOnly(True)
        self.layout.addWidget(description_widget)

        self.webView = QWebEngineView(self)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PluginsEnabled, True)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PdfViewerEnabled, True)
        self.layout.addWidget(self.webView)

        self.canvas = FigureCanvas(Figure(figsize=(5.0, 4.0), dpi=100))
        self.ax = self.canvas.figure.subplots()
        self.layout.addWidget(self.canvas)

    def update_variables(self, variables: list):
        self.covariate = ""
        self.response = ""

        self.covariate_combo_box.clear()
        self.covariate_combo_box.addItems(variables)
        self.covariate_combo_box.setCurrentText("")

        self.response_combo_box.clear()
        self.response_combo_box.addItems(variables)
        self.response_combo_box.setCurrentText("")

    def _analyze(self):
        if len(Manager.data.selected_groups) == 0:
            return

        df = Manager.data.selected_dataset.filter_by_groups(Manager.data.selected_groups)

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
        self.webView.setHtml("")
        self.ax.clear()

    def _covariate_current_text_changed(self, covariate: str):
        self.covariate = covariate

    def _response_current_text_changed(self, response: str):
        self.response = response

    @property
    def toolbar(self) -> QToolBar:
        toolbar = QToolBar()
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        toolbar.addWidget(QLabel("Covariate: "))
        self.covariate_combo_box.currentTextChanged.connect(self._covariate_current_text_changed)
        toolbar.addWidget(self.covariate_combo_box)

        toolbar.addWidget(QLabel("Response: "))
        self.response_combo_box.currentTextChanged.connect(self._response_current_text_changed)
        toolbar.addWidget(self.response_combo_box)

        pushButtonAnalyze = QPushButton("Analyze")
        pushButtonAnalyze.clicked.connect(self._analyze)
        toolbar.addWidget(pushButtonAnalyze)

        return toolbar
