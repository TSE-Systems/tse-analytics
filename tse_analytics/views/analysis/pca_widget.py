from typing import Optional

import plotly.express as px
from PySide6.QtCore import QTemporaryFile, QDir, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QComboBox, QLabel, QWidget
from sklearn.decomposition import PCA

from tse_analytics.core.manager import Manager
from tse_analytics.views.analysis.analysis_widget import AnalysisWidget


class PcaWidget(AnalysisWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.help_path = "docs/pca.md"

        self.components_combo_box = QComboBox(self)
        self.components_combo_box.addItems(["2D", "3D"])
        self.components_combo_box.setCurrentText("2D")
        self.toolbar.addWidget(QLabel("Dimensions: "))
        self.toolbar.addWidget(self.components_combo_box)

        self.web_view = QWebEngineView(self)
        self.web_view.settings().setAttribute(self.web_view.settings().WebAttribute.PluginsEnabled, False)
        self.web_view.settings().setAttribute(self.web_view.settings().WebAttribute.PdfViewerEnabled, False)
        self.web_view.setHtml("")
        self.layout().addWidget(self.web_view)

    def _analyze(self):
        selected_variables = Manager.data.selected_variables
        if len(selected_variables) < 3:
            return

        df = Manager.data.selected_dataset.active_df.dropna()
        features = [item.name for item in selected_variables]
        n_components = 2 if self.components_combo_box.currentText() == "2D" else 3

        pca = PCA(n_components=n_components)
        components = pca.fit_transform(df[features])

        total_var = pca.explained_variance_ratio_.sum() * 100

        if n_components == 2:
            fig = px.scatter(
                components,
                x=0,
                y=1,
                color=df["Group"],
                title=f"Total Explained Variance: {total_var:.2f}%",
                labels={"0": "PC 1", "1": "PC 2"},
            )
            self.web_view.setHtml(fig.to_html(include_plotlyjs="cdn"))
        elif n_components == 3:
            fig = px.scatter_3d(
                components,
                x=0,
                y=1,
                z=2,
                color=df["Group"],
                title=f"Total Explained Variance: {total_var:.2f}%",
                labels={"0": "PC 1", "1": "PC 2", "2": "PC 3"},
            )

            file = QTemporaryFile(f"{QDir.tempPath()}/XXXXXX.html", self)
            if file.open():
                fig.write_html(file.fileName(), include_plotlyjs=True)
                self.web_view.load(QUrl.fromLocalFile(file.fileName()))

    def clear(self):
        self.web_view.setHtml("")
