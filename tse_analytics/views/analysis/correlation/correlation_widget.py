import pingouin as pg
import seaborn as sns
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from pyqttoast import ToastPreset
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget

from tse_analytics.core import messaging
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.helper import get_html_image, show_help
from tse_analytics.core.toaster import make_toast
from tse_analytics.css import style_descriptive_table
from tse_analytics.modules.phenomaster.data.dataset import Dataset
from tse_analytics.views.analysis.correlation.correlation_widget_ui import Ui_CorrelationWidget


class CorrelationWidget(QWidget):
    def __init__(self, dataset: Dataset, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_CorrelationWidget()
        self.ui.setupUi(self)

        self.title = "Correlation"
        self.help_path = "Correlation.md"

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

        self.plot_toolbar = NavigationToolbar2QT(self.ui.canvas, self)
        self.plot_toolbar.setIconSize(QSize(16, 16))
        self.ui.widgetSettings.layout().addWidget(self.plot_toolbar)

        self.ui.textEdit.document().setDefaultStyleSheet(style_descriptive_table)

        self.dataset = dataset
        self.ui.variableSelectorX.set_data(self.dataset.variables)
        self.ui.variableSelectorY.set_data(self.dataset.variables)
        self.ui.factorSelector.set_data(self.dataset.factors, add_empty_item=False)

    def _update(self):
        x_var = self.ui.variableSelectorX.get_selected_variable()
        y_var = self.ui.variableSelectorY.get_selected_variable()
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
            if selected_factor_name == "":
                make_toast(
                    self,
                    self.title,
                    "Please select a factor.",
                    duration=2000,
                    preset=ToastPreset.WARNING,
                    show_duration_bar=True,
                ).show()
                return
            by = selected_factor_name

        variables = {x_var.name: x_var} if x_var.name == y_var.name else {x_var.name: x_var, y_var.name: y_var}
        df = self.dataset.get_current_df(
            variables=variables,
            split_mode=split_mode,
            selected_factor_name=selected_factor_name,
            dropna=False,
        )

        if split_mode != SplitMode.TOTAL and split_mode != SplitMode.RUN:
            df[by] = df[by].cat.remove_unused_categories()

        joint_grid = sns.jointplot(
            data=df,
            x=x_var.name,
            y=y_var.name,
            hue=by,
            marker=".",
        )
        joint_grid.fig.suptitle(f"Correlation between {x_var.name} and {y_var.name}")
        canvas = FigureCanvasQTAgg(joint_grid.figure)
        canvas.updateGeometry()
        canvas.draw()
        self.ui.splitterVertical.replaceWidget(0, canvas)

        # Assign canvas to PlotToolbar
        new_toolbar = NavigationToolbar2QT(canvas, self)
        new_toolbar.setIconSize(QSize(16, 16))
        self.ui.widgetSettings.layout().replaceWidget(self.plot_toolbar, new_toolbar)
        self.plot_toolbar.deleteLater()
        self.plot_toolbar = new_toolbar

        t_test = pg.ttest(df[x_var.name], df[y_var.name])
        corr = pg.pairwise_corr(data=df, columns=[x_var.name, y_var.name], method="pearson")

        html_template = """
            <h2>t-test</h2>
            {t_test}
            <h2>Pearson correlation</h2>
            {corr}
            """

        html = html_template.format(
            t_test=t_test.to_html(),
            corr=corr.to_html(),
        )
        self.ui.textEdit.document().setHtml(html)

    def _add_report(self):
        html = get_html_image(self.plot_toolbar.canvas.figure)
        html += self.ui.textEdit.toHtml()
        messaging.broadcast(messaging.AddToReportMessage(self, html, self.dataset))
