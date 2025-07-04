import seaborn as sns
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar, QComboBox, QLabel
from matplotlib.backends.backend_qt import NavigationToolbar2QT

from tse_analytics.core import messaging, color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.utils import get_html_image, get_h_spacer_widget
from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.variable_selector import VariableSelector


class DistributionWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Distribution"

        self.datatable = datatable

        # Setup toolbar
        toolbar = QToolBar(
            "Distribution Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        toolbar.addAction(QIcon(":/icons/icons8-refresh-16.png"), "Update").triggered.connect(self._update)
        toolbar.addSeparator()

        self.variableSelector = VariableSelector(toolbar)
        self.variableSelector.set_data(self.datatable.variables)
        toolbar.addWidget(self.variableSelector)

        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Group by:"))
        self.group_by_selector = GroupBySelector(toolbar, self.datatable, check_binning=False)
        toolbar.addWidget(self.group_by_selector)

        self.plot_type_combobox = QComboBox(toolbar)
        self.plot_type_combobox.addItems(["Violin plot", "Box plot"])
        toolbar.addWidget(self.plot_type_combobox)

        # Insert toolbar to the widget
        self.layout.addWidget(toolbar)

        self.canvas = MplCanvas(self)
        self.layout.addWidget(self.canvas)

        plot_toolbar = NavigationToolbar2QT(self.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        toolbar.addWidget(plot_toolbar)

        toolbar.addWidget(get_h_spacer_widget(toolbar))
        toolbar.addAction("Add to Report").triggered.connect(self._add_report)

    def _update(self):
        split_mode, selected_factor_name = self.group_by_selector.get_group_by()
        variable = self.variableSelector.get_selected_variable()

        match split_mode:
            case SplitMode.ANIMAL:
                x = "Animal"
                palette = color_manager.get_animal_to_color_dict(self.datatable.dataset.animals)
            case SplitMode.RUN:
                x = "Run"
                palette = color_manager.colormap_name
            case SplitMode.FACTOR:
                x = selected_factor_name
                palette = color_manager.get_level_to_color_dict(self.datatable.dataset.factors[selected_factor_name])
            case _:
                x = None
                palette = color_manager.colormap_name

        df = self.datatable.get_df(
            [variable.name],
            split_mode,
            selected_factor_name,
        )

        if split_mode != SplitMode.TOTAL and split_mode != SplitMode.RUN:
            df[x] = df[x].cat.remove_unused_categories()

        self.canvas.clear(False)
        ax = self.canvas.figure.add_subplot(111)
        ax.tick_params(axis="x", rotation=90)

        if self.plot_type_combobox.currentText() == "Violin plot":
            sns.violinplot(
                data=df,
                x=x,
                y=variable.name,
                hue=x,
                palette=palette,
                legend=False,
                ax=ax,
            )
        else:
            sns.boxplot(
                data=df,
                x=x,
                y=variable.name,
                hue=x,
                palette=palette,
                legend=False,
                gap=0.1,
                ax=ax,
            )

        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def _add_report(self):
        self.datatable.dataset.report += get_html_image(self.canvas.figure)
        messaging.broadcast(messaging.AddToReportMessage(self, self.datatable.dataset))
