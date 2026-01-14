from dataclasses import dataclass

from PySide6.QtCore import QSettings, QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QInputDialog, QLabel, QToolBar, QVBoxLayout, QWidget

from tse_analytics.core import manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.report import Report
from tse_analytics.core.utils import get_figsize_from_widget, get_h_spacer_widget
from tse_analytics.toolbox.correlation.processor import get_correlation_result
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.report_edit import ReportEdit
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
        toolbar = QToolBar(
            "Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        toolbar.addAction(QIcon(":/icons/icons8-refresh-16.png"), "Update").triggered.connect(self._update)
        toolbar.addSeparator()

        toolbar.addWidget(QLabel("X:"))
        self.xVariableSelector = VariableSelector(toolbar)
        self.xVariableSelector.set_data(self.datatable.variables, self._settings.x_variable)
        toolbar.addWidget(self.xVariableSelector)

        toolbar.addWidget(QLabel("Y:"))
        self.yVariableSelector = VariableSelector(toolbar)
        self.yVariableSelector.set_data(self.datatable.variables, self._settings.y_variable)
        toolbar.addWidget(self.yVariableSelector)

        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Group by:"))
        self.group_by_selector = GroupBySelector(toolbar, self.datatable, selected_mode=self._settings.group_by)
        toolbar.addWidget(self.group_by_selector)

        # Insert toolbar to the widget
        self._layout.addWidget(toolbar)

        self.report_view = ReportEdit(self)
        self._layout.addWidget(self.report_view)

        toolbar.addWidget(get_h_spacer_widget(toolbar))
        toolbar.addAction("Add Report").triggered.connect(self._add_report)

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

    def _update(self):
        self.report_view.clear()

        split_mode, selected_factor_name = self.group_by_selector.get_group_by()

        x_var = self.xVariableSelector.get_selected_variable()
        y_var = self.yVariableSelector.get_selected_variable()

        variable_columns = [x_var.name] if x_var.name == y_var.name else [x_var.name, y_var.name]
        df = self.datatable.get_df(
            variable_columns,
            split_mode,
            selected_factor_name,
        )

        result = get_correlation_result(
            self.datatable.dataset,
            df,
            x_var.name,
            y_var.name,
            split_mode,
            selected_factor_name,
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
