import plotly.express as px
from PySide6.QtCore import QDir, QTemporaryFile, QUrl
from PySide6.QtWidgets import QWidget
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

from tse_analytics.core.data.shared import GroupingMode
from tse_analytics.core.helper import show_help
from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import DatasetChangedMessage
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.messaging.messenger_listener import MessengerListener
from tse_analytics.views.analysis.dimensionality_widget_ui import Ui_DimensionalityWidget
from tse_analytics.views.misc.toast import Toast


class DimensionalityWidget(QWidget, MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_DimensionalityWidget()
        self.ui.setupUi(self)

        self.help_path = "dimensionality.md"
        self.ui.pushButtonHelp.clicked.connect(lambda: show_help(self, self.help_path))
        self.ui.pushButtonUpdate.clicked.connect(self.__update)

        self.ui.radioButtonMatrixPlot.toggled.connect(lambda: self.ui.groupBoxDimensions.setEnabled(False))
        self.ui.radioButtonPCA.toggled.connect(lambda: self.ui.groupBoxDimensions.setEnabled(True))
        self.ui.radioButtonTSNE.toggled.connect(lambda: self.ui.groupBoxDimensions.setEnabled(True))

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        self.ui.pushButtonUpdate.setDisabled(message.data is None)
        self.__clear()
        if message.data is not None:
            self.ui.factorSelector.set_data(message.data.factors)

    def __clear(self):
        self.ui.factorSelector.clear()
        self.ui.webView.setHtml("")

    def __update(self):
        if self.ui.radioButtonMatrixPlot.isChecked():
            self.__update_matrix_plot()
        elif self.ui.radioButtonPCA.isChecked():
            self.__update_pca_tsne_plot()
        elif self.ui.radioButtonTSNE.isChecked():
            self.__update_pca_tsne_plot()

    def __update_matrix_plot(self):
        if len(Manager.data.selected_variables) < 2:
            Toast(text="Please select at least two variables.", parent=self, duration=2000).show_toast()
            return

        selected_factor = self.ui.factorSelector.currentText()
        if self.ui.groupBoxFactor.isChecked() and selected_factor == "":
            Toast(text="Please select factor first.", parent=self, duration=2000).show_toast()
            return

        color = selected_factor if self.ui.groupBoxFactor.isChecked() else "Animal"

        variables = [variable.name for variable in Manager.data.selected_variables]
        df = Manager.data.get_current_df(
            variables=variables,
            grouping_mode=GroupingMode.ANIMALS,
            selected_factor=None,
            dropna=False,
        )

        fig = px.scatter_matrix(df, dimensions=variables, color=color)
        fig.update_traces(diagonal_visible=False)

        file = QTemporaryFile(f"{QDir.tempPath()}/XXXXXX.html", self)
        if file.open():
            fig.write_html(file.fileName(), include_plotlyjs=True)
            self.ui.webView.load(QUrl.fromLocalFile(file.fileName()))

    def __update_pca_tsne_plot(self):
        selected_factor = self.ui.factorSelector.currentText()
        if self.ui.groupBoxFactor.isChecked() and selected_factor == "":
            Toast(text="Please select factor first.", parent=self, duration=2000).show_toast()
            return

        if len(Manager.data.selected_variables) < 3:
            return

        color_column = selected_factor if self.ui.groupBoxFactor.isChecked() else "Animal"

        variables = [variable.name for variable in Manager.data.selected_variables]
        df = Manager.data.get_current_df(
            variables=variables,
            grouping_mode=GroupingMode.ANIMALS,
            selected_factor=None,
            dropna=True,
        )

        n_components = 2 if self.ui.radioButton2D.isChecked() else 3

        if self.ui.radioButtonPCA.isChecked():
            pca = PCA(n_components=n_components)
            data = pca.fit_transform(df[variables])
            total_var = pca.explained_variance_ratio_.sum() * 100
            title = f"Total Explained Variance: {total_var:.2f}%"
        elif self.ui.radioButtonTSNE.isChecked():
            tsne = TSNE(n_components=n_components, random_state=0)
            data = tsne.fit_transform(df[variables])
            title = "tSNE"

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
