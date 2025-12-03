from dataclasses import dataclass

import pingouin as pg
import seaborn.objects as so
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from PySide6.QtCore import QSettings, QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QSplitter, QTextEdit, QToolBar, QVBoxLayout, QWidget

from tse_analytics.core import color_manager, manager
from tse_analytics.core.data.binning import TimeIntervalsBinningSettings
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.pipeline.time_intervals_binning_pipe_operator import process_time_interval_binning
from tse_analytics.core.data.report import Report
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.utils import get_h_spacer_widget, get_html_image_from_figure
from tse_analytics.styles.css import style_descriptive_table
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class RegressionWidgetSettings:
    group_by: str = "Animal"
    covariate_variable: str = None
    response_variable: str = None


class RegressionWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        # Connect destructor to unsubscribe and save settings
        self.destroyed.connect(lambda: self._destroyed())

        # Settings management
        settings = QSettings()
        self._settings: RegressionWidgetSettings = settings.value(self.__class__.__name__, RegressionWidgetSettings())

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Regression"

        self.datatable = datatable

        # Setup toolbar
        toolbar = QToolBar(
            "Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        toolbar.addAction(QIcon(":/icons/icons8-refresh-16.png"), "Update").triggered.connect(self._update)
        toolbar.addSeparator()

        toolbar.addWidget(QLabel("Covariate:"))
        self.covariateVariableSelector = VariableSelector(toolbar)
        self.covariateVariableSelector.set_data(self.datatable.variables, self._settings.covariate_variable)
        toolbar.addWidget(self.covariateVariableSelector)

        toolbar.addWidget(QLabel("Response:"))
        self.responseVariableSelector = VariableSelector(toolbar)
        self.responseVariableSelector.set_data(self.datatable.variables, self._settings.response_variable)
        toolbar.addWidget(self.responseVariableSelector)

        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Group by:"))
        self.group_by_selector = GroupBySelector(toolbar, self.datatable, selected_mode=self._settings.group_by)
        toolbar.addWidget(self.group_by_selector)

        # Insert toolbar to the widget
        self._layout.addWidget(toolbar)

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

        plot_toolbar = NavigationToolbar2QT(self.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        toolbar.addWidget(plot_toolbar)

        toolbar.addWidget(get_h_spacer_widget(toolbar))
        toolbar.addAction("Add to Report").triggered.connect(self._add_report)

    def _destroyed(self):
        settings = QSettings()
        settings.setValue(
            self.__class__.__name__,
            RegressionWidgetSettings(
                self.group_by_selector.currentText(),
                self.covariateVariableSelector.currentText(),
                self.responseVariableSelector.currentText(),
            ),
        )

    def _update(self):
        # Clear the plot
        self.canvas.clear(False)

        split_mode, selected_factor_name = self.group_by_selector.get_group_by()

        covariate = self.covariateVariableSelector.get_selected_variable()
        response = self.responseVariableSelector.get_selected_variable()

        variable_columns = [response.name] if response.name == covariate.name else [response.name, covariate.name]
        columns = self.datatable.get_default_columns() + list(self.datatable.dataset.factors) + variable_columns
        df = self.datatable.get_filtered_df(columns)

        # Group by animal
        df = process_time_interval_binning(
            df,
            TimeIntervalsBinningSettings("day", 365),
            {
                covariate.name: covariate,
                response.name: response,
            },
            origin=self.datatable.dataset.experiment_started,
        )

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

        (
            so.Plot(
                df,
                x=covariate.name,
                y=response.name,
                color=by,
            )
            .add(so.Dot())
            .add(
                so.Line(),  # adds the regression line
                so.PolyFit(order=1),
            )
            .scale(color=palette)
            .on(self.canvas.figure)
            .plot(True)
        )

        self.canvas.figure.tight_layout()
        self.canvas.draw()

        match split_mode:
            case SplitMode.ANIMAL:
                output = ""
            case SplitMode.FACTOR:
                output = ""
                for level in df[selected_factor_name].unique().tolist():
                    data = df[df[selected_factor_name] == level]
                    output = (
                        output
                        + f"<h3>Level: {level}</h3>"
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
                data = df
                output = pg.linear_regression(data[covariate.name], data[response.name], remove_na=True).to_html()

        html_template = """
                <h2>Linear Regression</h2>
                {output}
                """

        html = html_template.format(
            output=output,
        )
        self.textEdit.document().setHtml(html)

    def _add_report(self):
        html = get_html_image_from_figure(self.canvas.figure)
        html += self.textEdit.toHtml()

        manager.add_report(
            Report(
                self.datatable.dataset,
                self.title,
                html,
            )
        )
