import pingouin as pg
import seaborn as sns
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.helper import show_help, get_html_image
from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import AddToReportMessage, DatasetChangedMessage
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.messaging.messenger_listener import MessengerListener
from tse_analytics.css import style_descriptive_table
from tse_analytics.views.analysis.bivariate_widget_ui import Ui_BivariateWidget
from tse_analytics.views.misc.notification import Notification


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
        self.ui.pushButtonUpdate.setDisabled(message.data is None)
        self.ui.pushButtonAddReport.setDisabled(message.data is None)
        self._clear()
        if message.data is not None:
            self.ui.variableSelectorX.set_data(message.data.variables)
            self.ui.variableSelectorY.set_data(message.data.variables)
            self.ui.factorSelector.set_data(message.data.factors, add_empty_item=False)

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
        x_var = self.ui.variableSelectorX.currentText()
        y_var = self.ui.variableSelectorY.currentText()
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
            if selected_factor == "":
                Notification(text="Please select factor.", parent=self, duration=2000).show_notification()
                return
            by = selected_factor

        variables = [x_var] if x_var == y_var else [x_var, y_var]
        df = Manager.data.get_current_df(
            variables=variables,
            split_mode=split_mode,
            selected_factor=selected_factor,
            dropna=False,
        )

        if split_mode != SplitMode.TOTAL and split_mode != SplitMode.RUN:
            df[by] = df[by].cat.remove_unused_categories()

        joint_grid = sns.jointplot(data=df, x=x_var, y=y_var, hue=by)
        joint_grid.fig.suptitle(f"Correlation between {x_var} and {y_var}")
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

        t_test = pg.ttest(df[x_var], df[y_var])
        corr = pg.pairwise_corr(data=df, columns=[x_var, y_var], method="pearson")

        html_template = """
            <h1>t-test</h1>
            {t_test}
            <h1>Pearson correlation</h1>
            {corr}
            """

        html = html_template.format(
            t_test=t_test.to_html(),
            corr=corr.to_html(),
        )
        self.ui.textEdit.document().setHtml(html)

    def _update_regression(self):
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

        if split_mode == SplitMode.ANIMAL:
            Notification(text="Please select another split mode.", parent=self, duration=2000).show_notification()
            return

        if split_mode == SplitMode.FACTOR and selected_factor == "":
            Notification(text="Please select factor.", parent=self, duration=2000).show_notification()
            return

        covariate = self.ui.variableSelectorX.currentText()
        response = self.ui.variableSelectorY.currentText()

        variables = [response] if response == covariate else [response, covariate]
        df = Manager.data.get_current_df(
            variables=variables,
            split_mode=split_mode,
            selected_factor=selected_factor,
            dropna=False,
        )

        agg = {
            covariate: "mean",
            response: "mean",
        }

        if selected_factor != "":
            agg[selected_factor] = "first"

        if split_mode == SplitMode.RUN:
            group_by = ["Animal", "Run"]
        else:
            group_by = ["Animal"]

        df = df.groupby(by=group_by, as_index=False, observed=False).agg(agg)

        facet_grid = sns.lmplot(data=df, x=covariate, y=response, hue=by, robust=False)
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

        glm = pg.linear_regression(df[[covariate]], df[response], remove_na=True)

        html_template = """
                <h1>GLM</h1>
                {glm}
                """

        html = html_template.format(
            glm=glm.to_html(),
        )
        self.ui.textEdit.document().setHtml(html)

    def _add_report(self):
        html = get_html_image(self.ui.canvas.figure)
        html += self.ui.textEdit.toHtml()

        Manager.messenger.broadcast(AddToReportMessage(self, html))
