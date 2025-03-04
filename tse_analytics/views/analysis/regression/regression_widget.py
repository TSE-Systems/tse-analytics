import pingouin as pg
import seaborn as sns
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QWidget, QToolBar, QVBoxLayout, QSplitter, QTextEdit, QWidgetAction, QLabel
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from pyqttoast import ToastPreset

from tse_analytics.core import messaging
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.helper import get_html_image, get_h_spacer_widget
from tse_analytics.core.toaster import make_toast
from tse_analytics.styles.css import style_descriptive_table
from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.split_mode_selector import SplitModeSelector
from tse_analytics.views.misc.variable_selector import VariableSelector


class RegressionWidget(QWidget):
    def __init__(self, dataset: Dataset, parent: QWidget | None = None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Regression"

        self.dataset = dataset
        self.split_mode = SplitMode.ANIMAL
        self.selected_factor_name = ""

        # Setup toolbar
        self.toolbar = QToolBar(
            "Data Plot Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        self.toolbar.addAction("Update").triggered.connect(self._update)
        self.toolbar.addSeparator()

        self.toolbar.addWidget(QLabel("Covariate:"))
        self.covariateVariableSelector = VariableSelector(self.toolbar)
        self.covariateVariableSelector.set_data(self.dataset.variables)
        self.toolbar.addWidget(self.covariateVariableSelector)

        self.toolbar.addWidget(QLabel("Response:"))
        self.responseVariableSelector = VariableSelector(self.toolbar)
        self.responseVariableSelector.set_data(self.dataset.variables)
        self.toolbar.addWidget(self.responseVariableSelector)

        split_mode_selector = SplitModeSelector(self.toolbar, self.dataset.factors, self._split_mode_callback)
        self.toolbar.addWidget(split_mode_selector)

        # Insert toolbar to the widget
        self.layout.addWidget(self.toolbar)

        self.splitter = QSplitter(
            self,
            orientation=Qt.Orientation.Vertical,
        )

        self.layout.addWidget(self.splitter)

        self.canvas = MplCanvas(self.splitter)
        self.splitter.addWidget(self.canvas)

        self.textEdit = QTextEdit(
            self.splitter,
            undoRedoEnabled=False,
            readOnly=True,
        )
        self.textEdit.document().setDefaultStyleSheet(style_descriptive_table)
        self.splitter.addWidget(self.textEdit)

        self.spacer_action = QWidgetAction(self.toolbar)
        self.spacer_action.setDefaultWidget(get_h_spacer_widget(self.toolbar))
        self.toolbar.addAction(self.spacer_action)

        self.toolbar.addAction("Add to Report").triggered.connect(self._add_report)
        self._add_plot_toolbar()

    def _split_mode_callback(self, mode: SplitMode, factor_name: str | None):
        self.split_mode = mode
        self.selected_factor_name = factor_name

    def _add_plot_toolbar(self):
        self.plot_toolbar_action = QWidgetAction(self.toolbar)
        plot_toolbar = NavigationToolbar2QT(self.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        self.plot_toolbar_action.setDefaultWidget(plot_toolbar)
        self.toolbar.insertAction(self.spacer_action, self.plot_toolbar_action)

    def _update(self):
        if self.split_mode == SplitMode.FACTOR and self.selected_factor_name == "":
            make_toast(
                self,
                self.title,
                "Please select a factor.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        match self.split_mode:
            case SplitMode.ANIMAL:
                by = "Animal"
            case SplitMode.RUN:
                by = "Run"
            case SplitMode.FACTOR:
                by = self.selected_factor_name
            case _:
                by = None

        covariate = self.covariateVariableSelector.get_selected_variable()
        response = self.responseVariableSelector.get_selected_variable()

        variables = (
            {response.name: response}
            if response.name == covariate.name
            else {response.name: response, covariate.name: covariate}
        )

        df = self.dataset.get_current_df(
            variables=variables,
            split_mode=self.split_mode,
            selected_factor_name=self.selected_factor_name,
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
        self.canvas = FigureCanvasQTAgg(facet_grid.figure)

        self.canvas.updateGeometry()
        self.canvas.draw()
        self.splitter.replaceWidget(0, self.canvas)

        # Assign canvas to PlotToolbar
        self.toolbar.removeAction(self.plot_toolbar_action)
        self._add_plot_toolbar()

        match self.split_mode:
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
                for group in df[self.selected_factor_name].unique().tolist():
                    data = df[df[self.selected_factor_name] == group]
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
        self.textEdit.document().setHtml(html)

    def _add_report(self):
        html = get_html_image(self.canvas.figure)
        html += self.textEdit.toHtml()
        self.dataset.report += html
        messaging.broadcast(messaging.AddToReportMessage(self, self.dataset))
