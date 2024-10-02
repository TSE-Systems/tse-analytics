import base64
from io import BytesIO

import plotly.express as px
from PySide6.QtCore import QBuffer, QByteArray, QDir, QIODevice, QTemporaryFile, QUrl
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QAbstractItemView
from pyqttoast import ToastPreset
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

from tse_analytics.core.data.shared import SplitMode, Variable
from tse_analytics.core.helper import show_help, make_toast
from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import AddToReportMessage, DatasetChangedMessage
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.messaging.messenger_listener import MessengerListener
from tse_analytics.core.workers.worker import Worker
from tse_analytics.views.analysis.dimensionality_widget_ui import Ui_DimensionalityWidget


class DimensionalityWidget(QWidget, MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_DimensionalityWidget()
        self.ui.setupUi(self)

        self.help_path = "dimensionality.md"

        self.ui.tableWidgetVariables.set_selection_mode(QAbstractItemView.SelectionMode.MultiSelection)

        self.ui.pushButtonHelp.clicked.connect(lambda: show_help(self, self.help_path))
        self.ui.pushButtonUpdate.clicked.connect(self._update)
        self.ui.pushButtonAddReport.clicked.connect(self._add_report)

        self.ui.radioButtonMatrixPlot.toggled.connect(
            lambda toggled: self.ui.groupBoxDimensions.setEnabled(False) if toggled else None
        )
        self.ui.radioButtonPCA.toggled.connect(
            lambda toggled: self.ui.groupBoxDimensions.setEnabled(True) if toggled else None
        )
        self.ui.radioButtonTSNE.toggled.connect(
            lambda toggled: self.ui.groupBoxDimensions.setEnabled(True) if toggled else None
        )

        self.ui.radioButtonSplitTotal.toggled.connect(
            lambda toggled: self.ui.factorSelector.setEnabled(False) if toggled else None
        )
        self.ui.radioButtonSplitByAnimal.toggled.connect(
            lambda toggled: self.ui.factorSelector.setEnabled(False) if toggled else None
        )
        self.ui.radioButtonSplitByFactor.toggled.connect(
            lambda toggled: self.ui.factorSelector.setEnabled(True) if toggled else None
        )
        self.ui.radioButtonSplitByRun.toggled.connect(
            lambda toggled: self.ui.factorSelector.setEnabled(False) if toggled else None
        )

        self.toast = None

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self._on_dataset_changed)

    def _on_dataset_changed(self, message: DatasetChangedMessage):
        self.ui.pushButtonUpdate.setDisabled(message.data is None)
        self.ui.pushButtonAddReport.setDisabled(message.data is None)
        self.ui.webView.setHtml("")
        if message.data is not None:
            self.ui.tableWidgetVariables.set_data(message.data.variables)
            self.ui.factorSelector.set_data(message.data.factors, add_empty_item=False)
        else:
            self.ui.tableWidgetVariables.clear_data()
            self.ui.factorSelector.clear()

    def _update(self):
        if self.ui.radioButtonMatrixPlot.isChecked():
            self._update_matrix_plot()
        elif self.ui.radioButtonPCA.isChecked():
            self._update_pca_tsne_plot()
        elif self.ui.radioButtonTSNE.isChecked():
            self._update_pca_tsne_plot()

    def _update_matrix_plot(self):
        selected_variables = self.ui.tableWidgetVariables.get_selected_variables_dict()
        if len(selected_variables) < 2:
            make_toast(
                self,
                "Dimensionality Analysis",
                "Please select at least two variables.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        selected_factor_name = self.ui.factorSelector.currentText()

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
            by = selected_factor_name

        if split_mode == SplitMode.FACTOR and selected_factor_name == "":
            make_toast(
                self,
                "Dimensionality Analysis",
                "Please select factor.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        df = Manager.data.get_current_df(
            variables=selected_variables,
            split_mode=split_mode,
            selected_factor_name=selected_factor_name,
            dropna=False,
        )

        fig = px.scatter_matrix(df, dimensions=list(selected_variables), color=by)
        fig.update_traces(diagonal_visible=False)

        file = QTemporaryFile(f"{QDir.tempPath()}/XXXXXX.html", self)
        if file.open():
            fig.write_html(file.fileName(), include_plotlyjs=True)
            self.ui.webView.load(QUrl.fromLocalFile(file.fileName()))

    def _update_pca_tsne_plot(self):
        selected_variables = self.ui.tableWidgetVariables.get_selected_variables_dict()
        if len(selected_variables) < 3:
            make_toast(
                self,
                "Dimensionality Analysis",
                "Please select at least three variables.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        selected_factor_name = self.ui.factorSelector.currentText()

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
            by = selected_factor_name

        if split_mode == SplitMode.FACTOR and selected_factor_name == "":
            make_toast(
                self,
                "Dimensionality Analysis",
                "Please select factor.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        self.ui.pushButtonUpdate.setEnabled(False)
        self.ui.pushButtonAddReport.setEnabled(False)

        self.toast = make_toast(self, "Dimensionality Analysis", "Processing...")
        self.toast.show()

        worker = Worker(self._calculate_pca_tsne, selected_variables, split_mode, selected_factor_name, by)
        worker.signals.result.connect(self._calculate_pca_tsne_result)
        worker.signals.finished.connect(self._calculate_pca_tsne_finished)
        Manager.threadpool.start(worker)

    def _calculate_pca_tsne(
        self,
        selected_variables: dict[str, Variable],
        split_mode: SplitMode,
        selected_factor_name: str,
        by: str,
    ) -> str:
        df = Manager.data.get_current_df(
            variables=selected_variables,
            split_mode=split_mode,
            selected_factor_name=selected_factor_name,
            dropna=True,
        )

        n_components = 2 if self.ui.radioButton2D.isChecked() else 3
        selected_variable_names = list(selected_variables)

        if self.ui.radioButtonPCA.isChecked():
            pca = PCA(n_components=n_components)
            data = pca.fit_transform(df[selected_variable_names])
            total_var = pca.explained_variance_ratio_.sum() * 100
            title = f"PCA. Total Explained Variance: {total_var:.2f}%"
        elif self.ui.radioButtonTSNE.isChecked():
            tsne = TSNE(n_components=n_components, random_state=0)
            data = tsne.fit_transform(df[selected_variable_names])
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
        return file.fileName()

    def _calculate_pca_tsne_result(self, filename: str):
        self.ui.webView.load(QUrl.fromLocalFile(filename))

    def _calculate_pca_tsne_finished(self):
        self.toast.hide()
        self.ui.pushButtonUpdate.setEnabled(True)
        self.ui.pushButtonAddReport.setEnabled(True)

    def _add_report(self):
        size = self.ui.webView.contentsRect()
        pixmap = QPixmap(size.width(), size.height())
        self.ui.webView.render(pixmap)

        ba = QByteArray()
        buffer = QBuffer(ba)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        pixmap.save(buffer, "PNG")

        io = BytesIO(ba.data())
        encoded = base64.b64encode(io.getvalue()).decode("utf-8")
        html = f"<img src='data:image/png;base64,{encoded}'>"
        Manager.messenger.broadcast(AddToReportMessage(self, html))
