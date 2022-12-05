import os.path
from typing import Optional

import plotly.express as px
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget, QToolBar, QPushButton, QLabel, QComboBox
from sklearn.decomposition import PCA

from tse_analytics.core.manager import Manager
from tse_analytics.views.analysis.analysis_widget import AnalysisWidget


class PcaWidget(AnalysisWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.components_combo_box = QComboBox(self)
        self.components_combo_box.addItems(['2D', '3D'])
        self.components_combo_box.setCurrentText('2D')

        self.layout.addWidget(self._get_toolbar())

        self.webView = QWebEngineView(self)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PluginsEnabled, True)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PdfViewerEnabled, True)
        self.layout.addWidget(self.webView)

    def _analyze(self):
        df = Manager.data.selected_dataset.original_df.dropna()
        selected_variables = Manager.data.selected_variables
        features = [item.name for item in selected_variables]
        n_components = 2 if self.components_combo_box.currentText() == '2D' else 3

        pca = PCA(n_components=n_components)
        components = pca.fit_transform(df[features])

        total_var = pca.explained_variance_ratio_.sum() * 100

        if n_components == 2:
            fig = px.scatter(
                components,
                x=0,
                y=1,
                color=df['Group'],
                title=f'Total Explained Variance: {total_var:.2f}%',
                labels={'0': 'PC 1', '1': 'PC 2'}
            )
            self.webView.setHtml(fig.to_html(include_plotlyjs='cdn'))
        elif n_components == 3:
            fig = px.scatter_3d(
                components,
                x=0,
                y=1,
                z=2,
                color=df['Group'],
                title=f'Total Explained Variance: {total_var:.2f}%',
                labels={'0': 'PC 1', '1': 'PC 2', '2': 'PC 3'}
            )
            self.webView.setHtml(fig.to_html(include_plotlyjs='cdn'))

    def clear(self):
        self.webView.setHtml('')

    @property
    def help_content(self) -> Optional[str]:
        path = 'docs/pca.md'
        if os.path.exists(path):
            with open(path, 'r') as file:
                return file.read().rstrip()

    def _get_toolbar(self) -> QToolBar:
        toolbar = super()._get_toolbar()

        label = QLabel("Dimensions: ")
        toolbar.addWidget(label)
        toolbar.addWidget(self.components_combo_box)

        pushButtonAnalyze = QPushButton("Analyze")
        pushButtonAnalyze.clicked.connect(self._analyze)
        toolbar.addWidget(pushButtonAnalyze)

        return toolbar
