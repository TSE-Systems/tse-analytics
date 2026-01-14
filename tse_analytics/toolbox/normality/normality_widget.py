from dataclasses import dataclass

from matplotlib.backends.backend_qt import NavigationToolbar2QT
from PySide6.QtCore import QSettings, QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QInputDialog, QLabel, QToolBar, QVBoxLayout, QWidget

from tse_analytics.core import manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.report import Report
from tse_analytics.core.utils import get_h_spacer_widget, get_html_image_from_figure
from tse_analytics.toolbox.normality.processor import test_normality
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class NormalityWidgetSettings:
    group_by: str = "Animal"
    selected_variable: str = None


class NormalityWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        # Connect destructor to unsubscribe and save settings
        self.destroyed.connect(lambda: self._destroyed())

        # Settings management
        settings = QSettings()
        self._settings: NormalityWidgetSettings = settings.value(self.__class__.__name__, NormalityWidgetSettings())

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Normality"

        self.datatable = datatable

        # Setup toolbar
        toolbar = QToolBar(
            "Data Plot Toolbar",
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
        toolbar.addAction("Add Report").triggered.connect(self._add_report)

    def _destroyed(self):
        settings = QSettings()
        settings.setValue(
            self.__class__.__name__,
            NormalityWidgetSettings(
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

        test_normality(
            df,
            variable.name,
            split_mode,
            selected_factor_name,
            self.canvas.figure,
        )

        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def _add_report(self):
        name, ok = QInputDialog.getText(
            self,
            "Report",
            "Please enter report name:",
            text=self.title,
        )
        if ok and name:
            manager.add_report(
                Report(
                    self.datatable.dataset,
                    name,
                    get_html_image_from_figure(self.canvas.figure),
                )
            )
