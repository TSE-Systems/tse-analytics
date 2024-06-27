import base64
from io import BytesIO

import plotly.express as px
from PySide6.QtCore import QDir, QMarginsF, Qt, QTemporaryFile, QUrl, QByteArray, QBuffer, QIODevice
from PySide6.QtGui import QPageLayout, QPageSize, QPixmap
from PySide6.QtWidgets import QWidget
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.helper import show_help
from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import AddToReportMessage, DatasetChangedMessage
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.messaging.messenger_listener import MessengerListener
from tse_analytics.views.analysis.dimensionality_widget_ui import Ui_DimensionalityWidget
from tse_analytics.views.misc.notification import Notification


class DimensionalityWidget(QWidget, MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_DimensionalityWidget()
        self.ui.setupUi(self)

        self.help_path = "dimensionality.md"

        self.ui.pushButtonHelp.clicked.connect(lambda: show_help(self, self.help_path))
        self.ui.pushButtonUpdate.clicked.connect(self.__update)
        self.ui.pushButtonAddReport.clicked.connect(self.__add_report)

        self.ui.radioButtonMatrixPlot.toggled.connect(lambda: self.ui.groupBoxDimensions.setEnabled(False))
        self.ui.radioButtonPCA.toggled.connect(lambda: self.ui.groupBoxDimensions.setEnabled(True))
        self.ui.radioButtonTSNE.toggled.connect(lambda: self.ui.groupBoxDimensions.setEnabled(True))

        self.ui.radioButtonSplitTotal.toggled.connect(lambda: self.ui.factorSelector.setEnabled(False))
        self.ui.radioButtonSplitByAnimal.toggled.connect(lambda: self.ui.factorSelector.setEnabled(False))
        self.ui.radioButtonSplitByFactor.toggled.connect(lambda: self.ui.factorSelector.setEnabled(True))
        self.ui.radioButtonSplitByRun.toggled.connect(lambda: self.ui.factorSelector.setEnabled(False))

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        self.ui.pushButtonUpdate.setDisabled(message.data is None)
        self.ui.pushButtonAddReport.setDisabled(message.data is None)
        self.__clear()
        if message.data is not None:
            self.ui.factorSelector.set_data(message.data.factors, add_empty_item=False)

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
            Notification(
                text="Please select at least two variables in Variables panel.", parent=self, duration=2000
            ).show_notification()
            return

        selected_factor = self.ui.factorSelector.currentText()

        split_mode = SplitMode.TOTAL
        by = None
        if self.ui.radioButtonSplitByAnimal.isChecked():
            split_mode = SplitMode.ANIMAL
            by = "Animal"
        elif self.ui.radioButtonSplitByRun.isChecked():
            split_mode = SplitMode.RUN
            by = "Run"
        elif self.ui.radioButtonSplitByFactor.isChecked():
            split_mode = SplitMode.FACTOR
            by = selected_factor

        if split_mode == SplitMode.FACTOR and selected_factor == "":
            Notification(text="Please select factor.", parent=self, duration=2000).show_notification()
            return

        variables = [variable.name for variable in Manager.data.selected_variables]
        df = Manager.data.get_current_df(
            variables=variables,
            split_mode=split_mode,
            selected_factor=selected_factor,
            dropna=False,
        )

        fig = px.scatter_matrix(df, dimensions=variables, color=by)
        fig.update_traces(diagonal_visible=False)

        file = QTemporaryFile(f"{QDir.tempPath()}/XXXXXX.html", self)
        if file.open():
            fig.write_html(file.fileName(), include_plotlyjs=True)
            self.ui.webView.load(QUrl.fromLocalFile(file.fileName()))

    def __update_pca_tsne_plot(self):
        if len(Manager.data.selected_variables) < 3:
            Notification(
                text="Please select at least three variables in Variables panel.", parent=self, duration=2000
            ).show_notification()
            return

        selected_factor = self.ui.factorSelector.currentText()

        split_mode = SplitMode.TOTAL
        by = None
        if self.ui.radioButtonSplitByAnimal.isChecked():
            split_mode = SplitMode.ANIMAL
            by = "Animal"
        elif self.ui.radioButtonSplitByRun.isChecked():
            split_mode = SplitMode.RUN
            by = "Run"
        elif self.ui.radioButtonSplitByFactor.isChecked():
            split_mode = SplitMode.FACTOR
            by = selected_factor

        if split_mode == SplitMode.FACTOR and selected_factor == "":
            Notification(text="Please select factor.", parent=self, duration=2000).show_notification()
            return

        variables = [variable.name for variable in Manager.data.selected_variables]
        df = Manager.data.get_current_df(
            variables=variables,
            split_mode=split_mode,
            selected_factor=selected_factor,
            dropna=True,
        )

        n_components = 2 if self.ui.radioButton2D.isChecked() else 3

        if self.ui.radioButtonPCA.isChecked():
            pca = PCA(n_components=n_components)
            data = pca.fit_transform(df[variables])
            total_var = pca.explained_variance_ratio_.sum() * 100
            title = f"PCA. Total Explained Variance: {total_var:.2f}%"
        elif self.ui.radioButtonTSNE.isChecked():
            tsne = TSNE(n_components=n_components, random_state=0)
            data = tsne.fit_transform(df[variables])
            title = "tSNE"

        if n_components == 2:
            fig = px.scatter(
                data,
                x=0,
                y=1,
                color=df[by] if by is not None else None,
                title=title,
                labels={
                    "0": "PC 1",
                    "1": "PC 2",
                    "color": by,
                },
                hover_name=df["Animal"],
            )
        elif n_components == 3:
            fig = px.scatter_3d(
                data,
                x=0,
                y=1,
                z=2,
                color=df[by] if by is not None else None,
                title=title,
                labels={
                    "0": "PC 1",
                    "1": "PC 2",
                    "2": "PC 3",
                    "color": by,
                },
                hover_name=df["Animal"],
            )

        file = QTemporaryFile(f"{QDir.tempPath()}/XXXXXX.html", self)
        if file.open():
            fig.write_html(file.fileName(), include_plotlyjs=True)
            self.ui.webView.load(QUrl.fromLocalFile(file.fileName()))

    def __add_report(self):
        size = self.ui.webView.contentsRect()
        pixmap = QPixmap(size.width(), size.height())
        self.ui.webView.render(pixmap)

        ba = QByteArray()
        buff = QBuffer(ba)
        buff.open(QIODevice.OpenModeFlag.WriteOnly)
        pixmap.save(buff, "PNG")

        io = BytesIO(ba.data())
        encoded = base64.b64encode(io.getvalue()).decode("utf-8")
        html = f"<img src='data:image/png;base64,{encoded}'>"
        Manager.messenger.broadcast(AddToReportMessage(self, html))
