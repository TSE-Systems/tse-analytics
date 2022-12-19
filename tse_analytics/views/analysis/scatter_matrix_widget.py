import tempfile
from typing import Optional

import plotly.express as px
from PySide6.QtCore import QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget

from tse_analytics.core.manager import Manager
from tse_analytics.views.analysis.analysis_widget import AnalysisWidget


class ScatterMatrixWidget(AnalysisWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.help_path = "docs/scatter-matrix.md"

        self.web_view = QWebEngineView()
        self.web_view.settings().setAttribute(self.web_view.settings().WebAttribute.PluginsEnabled, False)
        self.web_view.settings().setAttribute(self.web_view.settings().WebAttribute.PdfViewerEnabled, False)
        self.web_view.setHtml("")
        self.layout().addWidget(self.web_view)

    def _analyze(self):
        df = Manager.data.selected_dataset.original_df
        selected_variables = Manager.data.selected_variables
        features = [item.name for item in selected_variables]

        fig = px.scatter_matrix(df, dimensions=features, color="Group")
        fig.update_traces(diagonal_visible=False)

        tmp = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
        fig.write_html(tmp.name, include_plotlyjs=True)
        try:
            self.web_view.load(QUrl.fromLocalFile(tmp.name))
        finally:
            pass

    def clear(self):
        self.web_view.setHtml("")
