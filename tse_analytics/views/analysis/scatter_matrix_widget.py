import os.path
from typing import Optional

import plotly.express as px
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget, QToolBar, QPushButton

from tse_analytics.core.manager import Manager
from tse_analytics.views.analysis.analysis_widget import AnalysisWidget


class ScatterMatrixWidget(AnalysisWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.layout.addWidget(self._get_toolbar())

        self.webView = QWebEngineView(self)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PluginsEnabled, True)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PdfViewerEnabled, True)
        self.layout.addWidget(self.webView)

    def _analyze(self):
        df = Manager.data.selected_dataset.original_df
        selected_variables = Manager.data.selected_variables
        features = [item.name for item in selected_variables]

        fig = px.scatter_matrix(
            df,
            dimensions=features,
            color="Group"
        )
        fig.update_traces(diagonal_visible=False)

        self.webView.setHtml(fig.to_html(include_plotlyjs='cdn'))

    def clear(self):
        self.webView.setHtml('')

    @property
    def help_content(self) -> Optional[str]:
        path = 'docs/scatter-matrix.md'
        if os.path.exists(path):
            with open(path, 'r') as file:
                return file.read().rstrip()

    def _get_toolbar(self) -> QToolBar:
        toolbar = super()._get_toolbar()

        pushButtonAnalyze = QPushButton("Analyze")
        pushButtonAnalyze.clicked.connect(self._analyze)
        toolbar.addWidget(pushButtonAnalyze)

        return toolbar