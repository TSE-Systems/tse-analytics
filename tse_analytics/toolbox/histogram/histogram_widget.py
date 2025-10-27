from dataclasses import dataclass

import seaborn.objects as so
from PySide6.QtCore import QSize, Qt, QSettings
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar, QLabel
from matplotlib.backends.backend_qt import NavigationToolbar2QT

from tse_analytics.core import messaging, color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.utils import get_html_image_from_figure, get_h_spacer_widget
from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class HistogramWidgetSettings:
    group_by: str = "Animal"
    selected_variable: str = None


class HistogramWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        # Connect destructor to unsubscribe and save settings
        self.destroyed.connect(lambda: self._destroyed())

        # Settings management
        settings = QSettings()
        self._settings: HistogramWidgetSettings = settings.value(self.__class__.__name__, HistogramWidgetSettings())

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Histogram"

        self.datatable = datatable

        # Setup toolbar
        toolbar = QToolBar(
            "Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        toolbar.addAction(QIcon(":/icons/icons8-refresh-16.png"), "Update").triggered.connect(self._update)
        toolbar.addSeparator()

        self.variableSelector = VariableSelector(toolbar)
        self.variableSelector.set_data(self.datatable.variables, selected_variable=self._settings.selected_variable)
        toolbar.addWidget(self.variableSelector)

        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Group by:"))
        self.group_by_selector = GroupBySelector(toolbar, self.datatable, selected_mode=self._settings.group_by)
        toolbar.addWidget(self.group_by_selector)

        # Insert the toolbar to the widget
        self._layout.addWidget(toolbar)

        self.canvas = MplCanvas(self)
        self._layout.addWidget(self.canvas)

        plot_toolbar = NavigationToolbar2QT(self.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        toolbar.addWidget(plot_toolbar)

        toolbar.addWidget(get_h_spacer_widget(toolbar))
        toolbar.addAction("Add to Report").triggered.connect(self._add_report)

    def _destroyed(self):
        settings = QSettings()
        settings.setValue(
            self.__class__.__name__,
            HistogramWidgetSettings(
                self.group_by_selector.currentText(),
                self.variableSelector.currentText(),
            ),
        )

    def _update(self):
        # Clear the plot
        self.canvas.clear(False)

        split_mode, selected_factor_name = self.group_by_selector.get_group_by()
        variable = self.variableSelector.get_selected_variable()

        df = self.datatable.get_df(
            [variable.name],
            split_mode,
            selected_factor_name,
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
                x=variable.name,
                color=by,
            )
            .facet(col=by, wrap=3)
            .add(so.Bars(), so.Hist())
            .scale(color=palette)
            .on(self.canvas.figure)
            .plot(True)
        )

        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def _add_report(self) -> None:
        self.datatable.dataset.report += get_html_image_from_figure(self.canvas.figure)
        messaging.broadcast(messaging.AddToReportMessage(self, self.datatable.dataset))
