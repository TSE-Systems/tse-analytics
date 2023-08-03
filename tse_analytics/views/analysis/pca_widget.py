from typing import Optional

import plotly.express as px
from PySide6.QtCore import QTemporaryFile, QDir, QUrl
from PySide6.QtWidgets import QWidget
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
# from umap import UMAP

from tse_analytics.core.helper import show_help
from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import DatasetChangedMessage, ClearDataMessage
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.views.analysis.pca_widget_ui import Ui_PcaWidget


class PcaWidget(QWidget, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_PcaWidget()
        self.ui.setupUi(self)

        self.help_path = "docs/pca.md"
        self.ui.toolButtonHelp.clicked.connect(lambda: show_help(self, self.help_path))
        self.ui.toolButtonAnalyse.clicked.connect(self.__analyze)

        self.ui.comboBoxMethod.addItems(["PCA", "tSNE", "UMAP"])
        self.ui.comboBoxMethod.setCurrentText("PCA")

        self.ui.comboBoxDimensions.addItems(["2D", "3D"])
        self.ui.comboBoxDimensions.setCurrentText("2D")

        # self.ui.webView.settings().setAttribute(self.ui.webView.settings().WebAttribute.PluginsEnabled, False)
        # self.ui.webView.settings().setAttribute(self.ui.webView.settings().WebAttribute.PdfViewerEnabled, False)
        # self.ui.webView.setHtml("")

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)
        messenger.subscribe(self, ClearDataMessage, self.__on_clear_data)

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        self.__clear()

    def __on_clear_data(self, message: ClearDataMessage):
        self.__clear()

    def __clear(self):
        self.ui.webView.setHtml("")

    def __analyze(self):
        if Manager.data.selected_dataset is None or Manager.data.selected_factor is None:
            return

        if len(Manager.data.selected_variables) < 3:
            return

        factor_name = Manager.data.selected_factor.name

        variables = [variable.name for variable in Manager.data.selected_variables]
        df = Manager.data.get_current_df(calculate_error=False, variables=variables, dropna=True)

        method = self.ui.comboBoxMethod.currentText()
        n_components = 2 if self.ui.comboBoxDimensions.currentText() == "2D" else 3

        match method:
            case "PCA":
                pca = PCA(n_components=n_components)
                data = pca.fit_transform(df[variables])
                total_var = pca.explained_variance_ratio_.sum() * 100
                title = f"Total Explained Variance: {total_var:.2f}%"
            case "tSNE":
                tsne = TSNE(n_components=n_components, random_state=0)
                data = tsne.fit_transform(df[variables])
                title = "tSNE"
            case _:
                pca = PCA(n_components=n_components)
                data = pca.fit_transform(df[variables])
                total_var = pca.explained_variance_ratio_.sum() * 100
                title = f"Total Explained Variance: {total_var:.2f}%"
                # umap = UMAP(n_components=n_components, init='random', random_state=0)
                # data = umap.fit_transform(df[variables])
                # title = "UMAP"

        if n_components == 2:
            fig = px.scatter(
                data,
                x=0,
                y=1,
                color=df[factor_name],
                title=title,
                labels={"0": "PC 1", "1": "PC 2"},
            )
            self.ui.webView.setHtml(fig.to_html(include_plotlyjs="cdn"))
        elif n_components == 3:
            fig = px.scatter_3d(
                data,
                x=0,
                y=1,
                z=2,
                color=df[factor_name],
                title=title,
                labels={"0": "PC 1", "1": "PC 2", "2": "PC 3"},
            )

            file = QTemporaryFile(f"{QDir.tempPath()}/XXXXXX.html", self)
            if file.open():
                fig.write_html(file.fileName(), include_plotlyjs=True)
                self.ui.webView.load(QUrl.fromLocalFile(file.fileName()))
