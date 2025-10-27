from dataclasses import dataclass

import pingouin as pg
import seaborn as sns
from PySide6.QtCore import QSize, Qt, QSettings
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar, QLabel, QSplitter, QTextEdit, QWidgetAction
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from tse_analytics.core import messaging, color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.utils import get_html_image_from_figure, get_h_spacer_widget
from tse_analytics.styles.css import style_descriptive_table
from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class CorrelationWidgetSettings:
    group_by: str = "Animal"
    x_variable: str = None
    y_variable: str = None


class CorrelationWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        # Connect destructor to unsubscribe and save settings
        self.destroyed.connect(lambda: self._destroyed())

        # Settings management
        settings = QSettings()
        self._settings: CorrelationWidgetSettings = settings.value(self.__class__.__name__, CorrelationWidgetSettings())

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Correlation"

        self.datatable = datatable

        # Setup toolbar
        self.toolbar = QToolBar(
            "Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        self.toolbar.addAction(QIcon(":/icons/icons8-refresh-16.png"), "Update").triggered.connect(self._update)
        self.toolbar.addSeparator()

        self.toolbar.addWidget(QLabel("X:"))
        self.xVariableSelector = VariableSelector(self.toolbar)
        self.xVariableSelector.set_data(self.datatable.variables, self._settings.x_variable)
        self.toolbar.addWidget(self.xVariableSelector)

        self.toolbar.addWidget(QLabel("Y:"))
        self.yVariableSelector = VariableSelector(self.toolbar)
        self.yVariableSelector.set_data(self.datatable.variables, self._settings.y_variable)
        self.toolbar.addWidget(self.yVariableSelector)

        self.toolbar.addSeparator()
        self.toolbar.addWidget(QLabel("Group by:"))
        self.group_by_selector = GroupBySelector(self.toolbar, self.datatable, selected_mode=self._settings.group_by)
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

    def _destroyed(self):
        settings = QSettings()
        settings.setValue(
            self.__class__.__name__,
            CorrelationWidgetSettings(
                self.group_by_selector.currentText(),
                self.xVariableSelector.currentText(),
                self.yVariableSelector.currentText(),
            ),
        )

    def _add_plot_toolbar(self):
        self.plot_toolbar_action = QWidgetAction(self.toolbar)
        plot_toolbar = NavigationToolbar2QT(self.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        self.plot_toolbar_action.setDefaultWidget(plot_toolbar)
        self.toolbar.insertAction(self.spacer_action, self.plot_toolbar_action)

    def _update(self):
        split_mode, selected_factor_name = self.group_by_selector.get_group_by()

        x_var = self.xVariableSelector.get_selected_variable()
        y_var = self.yVariableSelector.get_selected_variable()

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

        variable_columns = [x_var.name] if x_var.name == y_var.name else [x_var.name, y_var.name]
        df = self.datatable.get_df(
            variable_columns,
            split_mode,
            selected_factor_name,
        )

        if split_mode != SplitMode.TOTAL and split_mode != SplitMode.RUN:
            df[by] = df[by].cat.remove_unused_categories()

        joint_grid = sns.jointplot(
            data=df,
            x=x_var.name,
            y=y_var.name,
            hue=by,
            palette=palette,
            marker=".",
        )
        joint_grid.figure.suptitle(f"Correlation between {x_var.name} and {y_var.name}")
        self.canvas = FigureCanvasQTAgg(joint_grid.figure)
        self.canvas.updateGeometry()
        self.canvas.draw()
        self.splitter.replaceWidget(0, self.canvas)

        # Assign canvas to PlotToolbar
        self.toolbar.removeAction(self.plot_toolbar_action)
        self._add_plot_toolbar()

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
        self.textEdit.document().setHtml(html)

    def _add_report(self):
        html = get_html_image_from_figure(self.canvas.figure)
        html += self.textEdit.toHtml()
        self.datatable.dataset.report += html
        messaging.broadcast(messaging.AddToReportMessage(self, self.datatable.dataset))
