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
from tse_analytics.views.analysis.regression.regression_widget_ui import Ui_RegressionWidget


class RegressionWidget(QWidget):
    def __init__(self, dataset: Dataset, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_RegressionWidget()
        self.ui.setupUi(self)

        self.title = "Regression"
        self.help_path = "regression.md"

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
        self.ui.variableSelectorCovariate.set_data(self.dataset.variables)
        self.ui.variableSelectorResponse.set_data(self.dataset.variables)
        self.ui.factorSelector.set_data(self.dataset.factors, add_empty_item=False)

    def _update(self):
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
                "Please select a factor.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        covariate = self.ui.variableSelectorCovariate.get_selected_variable()
        response = self.ui.variableSelectorResponse.get_selected_variable()

        variables = (
            {response.name: response}
            if response.name == covariate.name
            else {response.name: response, covariate.name: covariate}
        )
        df = self.dataset.get_current_df(
            variables=variables,
            split_mode=split_mode,
            selected_factor_name=selected_factor_name,
            dropna=False,
        )

        facet_grid = sns.lmplot(
            data=df,
            x=covariate.name,
            y=response.name,
            hue=by,
            robust=False,
            markers=".",
        )
        canvas = FigureCanvasQTAgg(facet_grid.figure)

        canvas.updateGeometry()
        canvas.draw()
        self.ui.splitterVertical.replaceWidget(0, canvas)

        # Assign canvas to PlotToolbar
        new_toolbar = NavigationToolbar2QT(canvas, self)
        new_toolbar.setIconSize(QSize(16, 16))
        self.ui.widgetSettings.layout().replaceWidget(self.plot_toolbar, new_toolbar)
        self.plot_toolbar.deleteLater()
        self.plot_toolbar = new_toolbar

        match split_mode:
            case SplitMode.ANIMAL:
                output = ""
                for animal in df["Animal"].unique().tolist():
                    data = df[df["Animal"] == animal]
                    output = (
                        output
                        + f"<h3>Animal: {animal}</h3>"
                        + pg.linear_regression(data[covariate.name], data[response.name], remove_na=True).to_html()
                    )
            case SplitMode.FACTOR:
                output = ""
                for group in df[selected_factor_name].unique().tolist():
                    data = df[df[selected_factor_name] == group]
                    output = (
                        output
                        + f"<h3>Group: {group}</h3>"
                        + pg.linear_regression(data[covariate.name], data[response.name], remove_na=True).to_html()
                    )
            case SplitMode.RUN:
                output = ""
                for run in df["Run"].unique().tolist():
                    data = df[df["Run"] == run]
                    output = (
                        output
                        + f"<h3>Run: {run}</h3>"
                        + pg.linear_regression(data[covariate.name], data[response.name], remove_na=True).to_html()
                    )
            case _:
                output = pg.linear_regression(df[covariate.name], df[response.name], remove_na=True).to_html()

        html_template = """
                <h2>Linear Regression</h2>
                {output}
                """

        html = html_template.format(
            output=output,
        )
        self.ui.textEdit.document().setHtml(html)

    def _add_report(self):
        html = get_html_image(self.plot_toolbar.canvas.figure)
        html += self.ui.textEdit.toHtml()
        messaging.broadcast(messaging.AddToReportMessage(self, html))
