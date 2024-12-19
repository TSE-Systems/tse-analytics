import pandas as pd
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from pyqttoast import ToastPreset
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QAbstractItemView, QWidget

from tse_analytics.core import messaging
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.helper import get_html_image, show_help
from tse_analytics.core.toaster import make_toast
from tse_analytics.modules.phenomaster.data.dataset import Dataset
from tse_analytics.views.analysis.matrixplot.matrixplot_widget_ui import Ui_MatrixPlotWidget


class MatrixPlotWidget(QWidget):
    def __init__(self, dataset: Dataset, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_MatrixPlotWidget()
        self.ui.setupUi(self)

        self.title = "Matrix Plot"
        self.help_path = "Matrix-Plot.md"

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
        if len(selected_variables) < 2:
            make_toast(
                self,
                self.title,
                "Please select at least two variables.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        selected_factor_name = self.ui.factorSelector.currentText()

        split_mode = SplitMode.TOTAL
        if self.ui.radioButtonSplitByAnimal.isChecked():
            split_mode = SplitMode.ANIMAL
        elif self.ui.radioButtonSplitByRun.isChecked():
            split_mode = SplitMode.RUN
        elif self.ui.radioButtonSplitByFactor.isChecked():
            split_mode = SplitMode.FACTOR

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

        df = self.dataset.get_current_df(
            variables=selected_variables,
            split_mode=split_mode,
            selected_factor_name=selected_factor_name,
            dropna=True,
        )

        match split_mode:
            case SplitMode.ANIMAL:
                colors, _ = pd.factorize(df["Animal"])
            case SplitMode.RUN:
                colors = df["Run"]
            case SplitMode.FACTOR:
                colors, _ = pd.factorize(df[selected_factor_name])
            case _:  # Total
                colors = None

        self.ui.canvas.clear(False)
        ax = self.ui.canvas.figure.add_subplot(111)

        pd.plotting.scatter_matrix(
            frame=df[list(selected_variables)],
            diagonal="hist",
            c=colors,
            ax=ax,
        )

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()

    def _add_report(self):
        self.dataset.report += get_html_image(self.ui.canvas.figure)
        messaging.broadcast(messaging.AddToReportMessage(self, self.dataset))
