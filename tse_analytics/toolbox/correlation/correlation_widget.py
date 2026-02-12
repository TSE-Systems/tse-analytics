from dataclasses import dataclass

from PySide6.QtWidgets import QLabel, QToolBar, QWidget

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.utils import get_figsize_from_widget
from tse_analytics.toolbox.correlation.processor import get_correlation_result
from tse_analytics.toolbox.toolbox_widget_base import ToolboxWidgetBase
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class CorrelationWidgetSettings:
    group_by: str = "Animal"
    x_variable: str = None
    y_variable: str = None


class CorrelationWidget(ToolboxWidgetBase):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(
            datatable,
            CorrelationWidgetSettings,
            title="Correlation",
            parent=parent,
        )

    def _create_toolbar_items(self, toolbar: QToolBar) -> None:
        toolbar.addWidget(QLabel("X:"))
        self.xVariableSelector = VariableSelector(toolbar)
        self.xVariableSelector.set_data(self.datatable.variables, selected_variable=self._settings.x_variable)
        toolbar.addWidget(self.xVariableSelector)

        toolbar.addWidget(QLabel("Y:"))
        self.yVariableSelector = VariableSelector(toolbar)
        self.yVariableSelector.set_data(self.datatable.variables, selected_variable=self._settings.y_variable)
        toolbar.addWidget(self.yVariableSelector)

        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Group by:"))
        self.group_by_selector = GroupBySelector(toolbar, self.datatable, selected_mode=self._settings.group_by)
        toolbar.addWidget(self.group_by_selector)

    def _get_settings_value(self):
        return CorrelationWidgetSettings(
            self.group_by_selector.currentText(),
            self.xVariableSelector.currentText(),
            self.yVariableSelector.currentText(),
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
