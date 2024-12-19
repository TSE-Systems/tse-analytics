import pingouin as pg
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from pyqttoast import ToastPreset
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget

from tse_analytics.core import messaging
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.helper import get_html_image, show_help
from tse_analytics.core.toaster import make_toast
from tse_analytics.modules.phenomaster.data.dataset import Dataset
from tse_analytics.views.analysis.normality.normality_widget_ui import Ui_NormalityWidget


class NormalityWidget(QWidget):
    def __init__(self, dataset: Dataset, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_NormalityWidget()
        self.ui.setupUi(self)

        self.title = "Normality"
        self.help_path = "Normality.md"

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

        self._update_normality_plot()

    def _update_normality_plot(self):
        variable = self.ui.variableSelector.get_selected_variable()
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

        df = self.dataset.get_current_df(
            variables={variable.name: variable},
            split_mode=split_mode,
            selected_factor_name=selected_factor_name,
            dropna=True,
        )

        if split_mode != SplitMode.TOTAL and split_mode != SplitMode.RUN:
            df[by] = df[by].cat.remove_unused_categories()

        self.ui.canvas.clear(False)

        match split_mode:
            case SplitMode.ANIMAL:
                animals = df["Animal"].unique()
                nrows, ncols = self._get_plot_layout(len(animals))
                for index, animal in enumerate(animals):
                    ax = self.ui.canvas.figure.add_subplot(nrows, ncols, index + 1)
                    pg.qqplot(
                        df[df["Animal"] == animal][variable.name],
                        dist="norm",
                        marker=".",
                        ax=ax,
                    )
                    ax.set_title(f"Animal: {animal}")
            case SplitMode.FACTOR:
                groups = df[selected_factor_name].unique()
                nrows, ncols = self._get_plot_layout(len(groups))
                for index, group in enumerate(groups):
                    # TODO: NaN check
                    if group != group:
                        continue
                    ax = self.ui.canvas.figure.add_subplot(nrows, ncols, index + 1)
                    pg.qqplot(
                        df[df[selected_factor_name] == group][variable.name],
                        dist="norm",
                        marker=".",
                        ax=ax,
                    )
                    ax.set_title(group)
            case SplitMode.RUN:
                runs = df["Run"].unique()
                nrows, ncols = self._get_plot_layout(len(runs))
                for index, run in enumerate(runs):
                    ax = self.ui.canvas.figure.add_subplot(nrows, ncols, index + 1)
                    pg.qqplot(
                        df[df["Run"] == run][variable.name],
                        dist="norm",
                        marker=".",
                        ax=ax,
                    )
                    ax.set_title(f"Run: {run}")
            case SplitMode.TOTAL:
                ax = self.ui.canvas.figure.add_subplot(1, 1, 1)
                pg.qqplot(
                    df[variable.name],
                    dist="norm",
                    marker=".",
                    ax=ax,
                )
                ax.set_title("Total")

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()

    def _get_plot_layout(self, number_of_elements: int):
        if number_of_elements == 1:
            return 1, 1
        elif number_of_elements == 2:
            return 1, 2
        elif number_of_elements <= 4:
            return 2, 2
        else:
            return round(number_of_elements / 3) + 1, 3

    def _add_report(self):
        self.dataset.report += get_html_image(self.ui.canvas.figure)
        messaging.broadcast(messaging.AddToReportMessage(self, self.dataset))
