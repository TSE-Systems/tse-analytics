from typing import Optional

import plotly.express as px
from PySide6.QtCore import QTemporaryFile, QDir, QUrl
from PySide6.QtWidgets import QWidget
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

# from umap import UMAP

from tse_analytics.core.helper import show_help
from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import DatasetChangedMessage
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.views.analysis.pca_widget_ui import Ui_PcaWidget
from tse_analytics.views.misc.toast import Toast
from tse_datatools.analysis.grouping_mode import GroupingMode


class PcaWidget(QWidget, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_PcaWidget()
        self.ui.setupUi(self)

        self.help_path = "pca.md"
        self.ui.toolButtonHelp.clicked.connect(lambda: show_help(self, self.help_path))
        self.ui.toolButtonAnalyse.clicked.connect(self.__analyze)

        # self.ui.comboBoxMethod.addItems(["PCA", "tSNE", "UMAP"])
        self.ui.comboBoxMethod.addItems(["PCA", "tSNE"])
        self.ui.comboBoxMethod.setCurrentText("PCA")

        self.ui.comboBoxDimensions.addItems(["2D", "3D"])
        self.ui.comboBoxDimensions.setCurrentText("2D")

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        self.ui.toolButtonAnalyse.setDisabled(message.data is None)
        self.__clear()

    def __clear(self):
        self.ui.webView.setHtml("")

    def __analyze(self):
        if Manager.data.grouping_mode == GroupingMode.FACTORS and Manager.data.selected_factor is None:
            Toast(text="Please select a factor first!", duration=2000, parent=self).show_toast()
            return

        if len(Manager.data.selected_variables) < 3:
            return

        match Manager.data.grouping_mode:
            case GroupingMode.FACTORS:
                color_column = Manager.data.selected_factor.name
            case GroupingMode.RUNS:
                color_column = "Run"
            case _:
                color_column = "Animal"

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
                # umap = UMAP(n_components=n_components, init='random')
                # data = umap.fit_transform(df[variables])
                # title = "UMAP"

        if n_components == 2:
            fig = px.scatter(
                data,
                x=0,
                y=1,
                color=df[color_column].astype(str),
                title=title,
                labels={
                    "0": "PC 1",
                    "1": "PC 2",
                    "color": color_column,
                },
                hover_name=df["Animal"],
            )
        elif n_components == 3:
            fig = px.scatter_3d(
                data,
                x=0,
                y=1,
                z=2,
                color=df[color_column],
                title=title,
                labels={
                    "0": "PC 1",
                    "1": "PC 2",
                    "2": "PC 3",
                    "color": color_column,
                },
                hover_name=df["Animal"],
            )

        file = QTemporaryFile(f"{QDir.tempPath()}/XXXXXX.html", self)
        if file.open():
            fig.write_html(file.fileName(), include_plotlyjs=True)
            self.ui.webView.load(QUrl.fromLocalFile(file.fileName()))
