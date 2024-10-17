import pingouin as pg
import seaborn as sns
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from pyqttoast import ToastPreset
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget

from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.helper import get_html_image, show_help
from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import AddToReportMessage, DatasetChangedMessage
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.messaging.messenger_listener import MessengerListener
from tse_analytics.core.toaster import make_toast
from tse_analytics.css import style_descriptive_table
from tse_analytics.views.analysis.bivariate_widget_ui import Ui_BivariateWidget


class BivariateWidget(QWidget, MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_BivariateWidget()
        self.ui.setupUi(self)

        self.help_path = "bivariate.md"

        self.ui.pushButtonHelp.clicked.connect(lambda: show_help(self, self.help_path))
        self.ui.pushButtonUpdate.clicked.connect(self._update)
        self.ui.pushButtonAddReport.clicked.connect(self._add_report)

        self.ui.radioButtonCorrelation.toggled.connect(self._correlation_selected)
        self.ui.radioButtonRegression.toggled.connect(self._regression_selected)

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

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self._on_dataset_changed)

    def _on_dataset_changed(self, message: DatasetChangedMessage):
        self.ui.pushButtonUpdate.setDisabled(message.dataset is None)
        self.ui.pushButtonAddReport.setDisabled(message.dataset is None)
        self._clear()
        if message.dataset is not None:
            self.ui.variableSelectorX.set_data(message.dataset.variables)
            self.ui.variableSelectorY.set_data(message.dataset.variables)
            self.ui.factorSelector.set_data(message.dataset.factors, add_empty_item=False)

    def _clear(self):
        self.ui.variableSelectorX.clear()
        self.ui.variableSelectorY.clear()
        self.ui.factorSelector.clear()
        self.ui.textEdit.document().clear()

    def _correlation_selected(self, toggled: bool):
        if not toggled:
            return
        self.ui.groupBoxX.setTitle("X")
        self.ui.groupBoxY.setTitle("Y")

    def _regression_selected(self, toggled: bool):
        if not toggled:
            return
        self.ui.groupBoxX.setTitle("Covariate")
        self.ui.groupBoxY.setTitle("Response")

    def _update(self):
        if self.ui.radioButtonCorrelation.isChecked():
            self._update_correlation()
        elif self.ui.radioButtonRegression.isChecked():
            self._update_regression()

    def _update_correlation(self):
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
                    "Bivariate Analysis",
                    "Please select a factor.",
                    duration=2000,
                    preset=ToastPreset.WARNING,
                    show_duration_bar=True,
                ).show()
                return
            by = selected_factor_name

        variables = {x_var.name: x_var} if x_var.name == y_var.name else {x_var.name: x_var, y_var.name: y_var}
        df = Manager.data.get_current_df(
            variables=variables,
            split_mode=split_mode,
            selected_factor_name=selected_factor_name,
            dropna=False,
        )

        if split_mode != SplitMode.TOTAL and split_mode != SplitMode.RUN:
            df[by] = df[by].cat.remove_unused_categories()

        joint_grid = sns.jointplot(data=df, x=x_var.name, y=y_var.name, hue=by)
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

    def _update_regression(self):
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

        if split_mode == SplitMode.ANIMAL:
            make_toast(
                self,
                "Regression Analysis",
                "Please select another split mode.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        if split_mode == SplitMode.FACTOR and selected_factor_name == "":
            make_toast(
                self,
                "Bivariate Analysis",
                "Please select a factor.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        covariate = self.ui.variableSelectorX.get_selected_variable()
        response = self.ui.variableSelectorY.get_selected_variable()

        variables = (
            {response.name: response}
            if response.name == covariate.name
            else {response.name: response, covariate.name: covariate}
        )
        df = Manager.data.get_current_df(
            variables=variables,
            split_mode=split_mode,
            selected_factor_name=selected_factor_name,
            dropna=False,
        )

        facet_grid = sns.lmplot(data=df, x=covariate.name, y=response.name, hue=by, robust=False)
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

        Manager.messenger.broadcast(AddToReportMessage(self, html))
