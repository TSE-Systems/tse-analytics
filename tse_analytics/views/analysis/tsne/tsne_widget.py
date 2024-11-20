import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from pyqttoast import ToastPreset
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QAbstractItemView, QWidget
from sklearn.manifold import TSNE

from tse_analytics.core import messaging
from tse_analytics.core.data.shared import SplitMode, Variable
from tse_analytics.core.helper import get_html_image, show_help
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.workers.task_manager import TaskManager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.modules.phenomaster.data.dataset import Dataset
from tse_analytics.views.analysis.tsne.tsne_widget_ui import Ui_TsneWidget


class TsneWidget(QWidget):
    def __init__(self, dataset: Dataset, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_TsneWidget()
        self.ui.setupUi(self)

        self.title = "tSNE"
        self.help_path = "tsne.md"

        self.ui.tableWidgetVariables.set_selection_mode(QAbstractItemView.SelectionMode.MultiSelection)

        self.ui.pushButtonHelp.clicked.connect(lambda: show_help(self, self.help_path))
        self.ui.pushButtonUpdate.clicked.connect(self._update)
        self.ui.pushButtonAddReport.clicked.connect(self._add_report)

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

        plot_toolbar = NavigationToolbar2QT(self.ui.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        self.ui.widgetSettings.layout().addWidget(plot_toolbar)

        self.dataset = dataset
        self.ui.tableWidgetVariables.set_data(self.dataset.variables)
        self.ui.factorSelector.set_data(self.dataset.factors, add_empty_item=False)

        self.toast = None

    def _update(self):
        selected_variables = self.ui.tableWidgetVariables.get_selected_variables_dict()
        if len(selected_variables) < 3:
            make_toast(
                self,
                self.title,
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
                self.title,
                "Please select factor.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        self.ui.pushButtonUpdate.setEnabled(False)
        self.ui.pushButtonAddReport.setEnabled(False)

        self.toast = make_toast(self, self.title, "Processing...")
        self.toast.show()

        worker = Worker(self._calculate, selected_variables, split_mode, selected_factor_name, by)
        worker.signals.result.connect(self._result)
        worker.signals.finished.connect(self._finished)
        TaskManager.start_task(worker)

    def _calculate(
        self,
        selected_variables: dict[str, Variable],
        split_mode: SplitMode,
        selected_factor_name: str,
        by: str,
    ) -> tuple[pd.DataFrame, str, str]:
        df = self.dataset.get_current_df(
            variables=selected_variables,
            split_mode=split_mode,
            selected_factor_name=selected_factor_name,
            dropna=True,
        )

        selected_variable_names = list(selected_variables)

        tsne = TSNE(n_components=2, random_state=0)
        data = tsne.fit_transform(df[selected_variable_names])
        title = "tSNE"

        result_df = pd.DataFrame(data=data, columns=["X", "Y"])
        if by is not None:
            result_df = pd.concat([result_df, df[[by]]], axis=1)

        return result_df, title, by

    def _result(self, result: tuple):
        self.ui.canvas.clear(False)
        ax = self.ui.canvas.figure.add_subplot(111)

        df, title, by = result

        sns.scatterplot(
            data=df,
            x="tSNE1",
            y="tSNE2",
            hue=by,
            marker=".",
            ax=ax,
        )
        ax.set_title(title)

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()

    def _finished(self):
        self.toast.hide()
        self.ui.pushButtonUpdate.setEnabled(True)
        self.ui.pushButtonAddReport.setEnabled(True)

    def _add_report(self):
        html = get_html_image(self.ui.canvas.figure)
        messaging.broadcast(messaging.AddToReportMessage(self, html, self.dataset))
