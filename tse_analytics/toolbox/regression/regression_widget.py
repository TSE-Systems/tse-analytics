import statsmodels.api as sm
import seaborn as sns
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QToolBar, QVBoxLayout, QSplitter, QTextEdit, QWidgetAction, QLabel
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from tse_analytics.core import messaging, color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.utils import get_html_image, get_h_spacer_widget
from tse_analytics.styles.css import style_descriptive_table
from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.variable_selector import VariableSelector


class RegressionWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Regression"

        self.datatable = datatable

        # Setup toolbar
        self.toolbar = QToolBar(
            "Data Plot Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        self.toolbar.addAction(QIcon(":/icons/icons8-refresh-16.png"), "Update").triggered.connect(self._update)
        self.toolbar.addSeparator()

        self.toolbar.addWidget(QLabel("Covariate:"))
        self.covariateVariableSelector = VariableSelector(self.toolbar)
        self.covariateVariableSelector.set_data(self.datatable.variables)
        self.toolbar.addWidget(self.covariateVariableSelector)

        self.toolbar.addWidget(QLabel("Response:"))
        self.responseVariableSelector = VariableSelector(self.toolbar)
        self.responseVariableSelector.set_data(self.datatable.variables)
        self.toolbar.addWidget(self.responseVariableSelector)

        self.toolbar.addSeparator()
        self.toolbar.addWidget(QLabel("Group by:"))
        self.group_by_selector = GroupBySelector(self.toolbar, self.datatable, check_binning=False)
        self.toolbar.addWidget(self.group_by_selector)

        # Insert toolbar to the widget
        self._layout.addWidget(self.toolbar)

        self.splitter = QSplitter(
            self,
            orientation=Qt.Orientation.Vertical,
        )

        self._layout.addWidget(self.splitter)

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

    def _add_plot_toolbar(self):
        self.plot_toolbar_action = QWidgetAction(self.toolbar)
        plot_toolbar = NavigationToolbar2QT(self.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        self.plot_toolbar_action.setDefaultWidget(plot_toolbar)
        self.toolbar.insertAction(self.spacer_action, self.plot_toolbar_action)

    def _update(self):
        split_mode, selected_factor_name = self.group_by_selector.get_group_by()

        match split_mode:
            case SplitMode.ANIMAL:
                by = "Animal"
                palette = color_manager.get_animal_to_color_dict(self.datatable.dataset.animals)
            case SplitMode.RUN:
                by = "Run"
                palette = color_manager.colormap_name
            case SplitMode.FACTOR:
                by = selected_factor_name
                palette = color_manager.get_level_to_color_dict(self.datatable.dataset.factors[selected_factor_name])
            case _:
                by = None
                palette = color_manager.colormap_name

        covariate = self.covariateVariableSelector.get_selected_variable()
        response = self.responseVariableSelector.get_selected_variable()

        variable_columns = [response.name] if response.name == covariate.name else [response.name, covariate.name]
        df = self.datatable.get_df(
            variable_columns,
            split_mode,
            selected_factor_name,
        )

        facet_grid = sns.lmplot(
            data=df,
            x=covariate.name,
            y=response.name,
            hue=by,
            palette=palette,
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

        match split_mode:
            case SplitMode.ANIMAL:
                output = ""
                for animal in df["Animal"].unique().tolist():
                    data = df[df["Animal"] == animal]
                    output = (
                        output
                        + f"<h3>Animal: {animal}</h3>"
                        + sm.OLS(df[response.name], df[covariate.name], missing="drop").fit().summary2().as_html()
                    )
            case SplitMode.FACTOR:
                output = ""
                for level in df[selected_factor_name].unique().tolist():
                    data = df[df[selected_factor_name] == level]
                    output = (
                        output
                        + f"<h3>Level: {level}</h3>"
                        + sm.OLS(df[response.name], df[covariate.name], missing="drop").fit().summary2().as_html()
                    )
            case SplitMode.RUN:
                output = ""
                for run in df["Run"].unique().tolist():
                    data = df[df["Run"] == run]
                    output = (
                        output
                        + f"<h3>Run: {run}</h3>"
                        + sm.OLS(df[response.name], df[covariate.name], missing="drop").fit().summary2().as_html()
                    )
            case _:
                output = sm.OLS(df[response.name], df[covariate.name], missing="drop").fit().summary2().as_html()
                # output = pg.linear_regression(df[covariate.name], df[response.name], remove_na=True).to_html()

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
        self.datatable.dataset.report += html
        messaging.broadcast(messaging.AddToReportMessage(self, self.datatable.dataset))
