from dataclasses import dataclass

from PySide6.QtCore import QSettings, QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QInputDialog, QLabel, QSpinBox, QToolBar, QVBoxLayout, QWidget

from tse_analytics.core import manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.report import Report
from tse_analytics.core.utils import get_figsize_from_widget, get_h_spacer_widget
from tse_analytics.toolbox.actogram.processor import get_actogram_result
from tse_analytics.views.misc.report_edit import ReportEdit
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class ActogramWidgetSettings:
    selected_variable: str = None
    bins_per_hour: int = 6


class ActogramWidget(QWidget):
    """Widget for visualizing activity patterns over time in a double-plotted actogram format.

    An actogram is a graphical representation of activity data over multiple days,
    typically used in chronobiology to visualize circadian rhythms. This widget
    creates a double-plotted actogram where each row represents two consecutive days,
    allowing for better visualization of activity patterns that cross midnight.
    """

    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        # Connect destructor to unsubscribe and save settings
        self.destroyed.connect(lambda: self._destroyed())

        # Settings management
        settings = QSettings()
        self._settings: ActogramWidgetSettings = settings.value(self.__class__.__name__, ActogramWidgetSettings())

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Actogram"

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

        toolbar.addWidget(QLabel("Bins per hour:"))
        self.bins_spin_box = QSpinBox(
            toolbar,
            minimum=1,
            maximum=60,
            singleStep=1,
            value=self._settings.bins_per_hour,
        )
        toolbar.addWidget(self.bins_spin_box)

        # Insert the toolbar to the widget
        self._layout.addWidget(toolbar)

        self.report_view = ReportEdit(self)
        self._layout.addWidget(self.report_view)

        toolbar.addWidget(get_h_spacer_widget(toolbar))
        toolbar.addAction("Add Report").triggered.connect(self._add_report)

    def _destroyed(self):
        settings = QSettings()
        settings.setValue(
            self.__class__.__name__,
            ActogramWidgetSettings(
                self.variableSelector.currentText(),
                self.bins_spin_box.value(),
            ),
        )

    def _update(self):
        self.report_view.clear()

        variable = self.variableSelector.get_selected_variable()

        columns = ["Animal", "DateTime", variable.name]
        df = self.datatable.get_filtered_df(columns)

        result = get_actogram_result(
            self.datatable.dataset,
            df,
            variable,
            self.bins_spin_box.value(),
            get_figsize_from_widget(self.report_view),
        )

        self.report_view.set_content(result.report)

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
                    self.report_view.toHtml(),
                )
            )
