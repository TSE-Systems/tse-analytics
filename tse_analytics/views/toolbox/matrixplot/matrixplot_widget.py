import seaborn as sns
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QWidget,
    QVBoxLayout,
    QToolBar,
    QAbstractScrollArea,
    QWidgetAction,
    QLabel,
)
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from pyqttoast import ToastPreset

from tse_analytics.core import messaging, color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_html_image, get_h_spacer_widget, get_widget_tool_button
from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.variables_table_widget import VariablesTableWidget


class MatrixPlotWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Matrix Plot"

        self.datatable = datatable

        self.toast = None

        # Setup toolbar
        self.toolbar = QToolBar(
            "Data Plot Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        self.toolbar.addAction(QIcon(":/icons/icons8-refresh-16.png"), "Update").triggered.connect(self._update)
        self.toolbar.addSeparator()

        self.variables_table_widget = VariablesTableWidget()
        self.variables_table_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.variables_table_widget.set_data(self.datatable.variables)
        self.variables_table_widget.setMaximumHeight(400)
        self.variables_table_widget.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        variables_button = get_widget_tool_button(
            self.toolbar,
            self.variables_table_widget,
            "Variables",
            QIcon(":/icons/variables.png"),
        )
        self.toolbar.addWidget(variables_button)

        self.toolbar.addSeparator()
        self.toolbar.addWidget(QLabel("Group by:"))
        self.group_by_selector = GroupBySelector(self.toolbar, self.datatable)
        self.toolbar.addWidget(self.group_by_selector)

        # Insert toolbar to the widget
        self.layout.addWidget(self.toolbar)

        self.canvas = MplCanvas(self)
        self.layout.addWidget(self.canvas)

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
        selected_variables = self.variables_table_widget.get_selected_variables_dict()
        if len(selected_variables) < 2:
            make_toast(
                self,
                self.title,
                "Please select at least two variables.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        split_mode, selected_factor_name = self.group_by_selector.get_group_by()

        if split_mode == SplitMode.FACTOR and selected_factor_name == "":
            make_toast(
                self,
                self.title,
                "Please select factor.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        df = self.datatable.get_preprocessed_df(
            variables=selected_variables,
            split_mode=split_mode,
            selected_factor_name=selected_factor_name,
            dropna=True,
        )

        match split_mode:
            case SplitMode.ANIMAL:
                hue = "Animal"
                palette = color_manager.get_animal_to_color_dict(self.datatable.dataset.animals)
            case SplitMode.RUN:
                hue = "Run"
                palette = color_manager.colormap_name
            case SplitMode.FACTOR:
                hue = selected_factor_name
                palette = color_manager.get_level_to_color_dict(self.datatable.dataset.factors[selected_factor_name])
            case _:  # Total
                hue = None
                palette = color_manager.colormap_name

        # pd.plotting.scatter_matrix(
        #     frame=df[list(selected_variables)],
        #     diagonal="hist",
        #     c=colors,
        #     ax=ax,
        # )

        pair_grid = sns.pairplot(
            df[[hue] + list(selected_variables)] if hue is not None else df[list(selected_variables)],
            hue=hue,
            palette=palette,
            markers=".",
        )

        canvas = FigureCanvasQTAgg(pair_grid.figure)
        canvas.updateGeometry()
        canvas.draw()
        self.layout.replaceWidget(self.canvas, canvas)
        self.canvas = canvas

        # Assign canvas to PlotToolbar
        self.toolbar.removeAction(self.plot_toolbar_action)
        self._add_plot_toolbar()

    def _add_report(self):
        self.datatable.dataset.report += get_html_image(self.canvas.figure)
        messaging.broadcast(messaging.AddToReportMessage(self, self.datatable.dataset))
