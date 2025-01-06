import seaborn as sns
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from pyqttoast import ToastPreset
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget

from tse_analytics.core import messaging
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.helper import get_html_image, show_help
from tse_analytics.core.toaster import make_toast
from tse_analytics.views.analysis.distribution.distribution_widget_ui import Ui_DistributionWidget


class DistributionWidget(QWidget):
    def __init__(self, dataset: Dataset, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_DistributionWidget()
        self.ui.setupUi(self)

        self.title = "Distribution"
        self.help_path = "Distribution.md"

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
        self.ui.variableSelector.set_data(self.dataset.variables)
        self.ui.factorSelector.set_data(self.dataset.factors, add_empty_item=False)

    def _update(self):
        if self.ui.radioButtonSplitByFactor.isChecked() and self.ui.factorSelector.currentText() == "":
            make_toast(
                self,
                self.title,
                "Please select a factor.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        self._update_distribution_plot()

    def _update_distribution_plot(self):
        variable = self.ui.variableSelector.get_selected_variable()
        selected_factor_name = self.ui.factorSelector.currentText()

        split_mode = SplitMode.TOTAL
        x = None
        if self.ui.radioButtonSplitByAnimal.isChecked():
            split_mode = SplitMode.ANIMAL
            x = "Animal"
        elif self.ui.radioButtonSplitByRun.isChecked():
            split_mode = SplitMode.RUN
            x = "Run"
        elif self.ui.radioButtonSplitByFactor.isChecked():
            split_mode = SplitMode.FACTOR
            x = selected_factor_name

        df = self.dataset.get_current_df(
            variables={variable.name: variable},
            split_mode=split_mode,
            selected_factor_name=selected_factor_name,
            dropna=False,
        )

        if split_mode != SplitMode.TOTAL and split_mode != SplitMode.RUN:
            df[x] = df[x].cat.remove_unused_categories()

        self.ui.canvas.clear(False)
        ax = self.ui.canvas.figure.add_subplot(111)

        if self.ui.radioButtonViolin.isChecked():
            sns.violinplot(data=df, x=x, y=variable.name, ax=ax)
        else:
            sns.boxplot(data=df, x=x, y=variable.name, gap=0.1, ax=ax)

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()

    def _add_report(self):
        self.dataset.report += get_html_image(self.ui.canvas.figure)
        messaging.broadcast(messaging.AddToReportMessage(self, self.dataset))
