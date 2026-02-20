from dataclasses import dataclass, field

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QAbstractScrollArea,
    QToolBar,
    QWidget,
)

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.utils import get_figsize_from_widget, get_widget_tool_button
from tse_analytics.toolbox.correlation_matrix.processor import get_correlation_matrix_result
from tse_analytics.toolbox.toolbox_registry import toolbox_plugin
from tse_analytics.toolbox.toolbox_widget_base import ToolboxWidgetBase
from tse_analytics.views.misc.variables_table_widget import VariablesTableWidget


@dataclass
class CorrelationMatrixWidgetSettings:
    selected_variables: list[str] = field(default_factory=list)


@toolbox_plugin(category="Factor Analysis", label="Correlation Matrix", icon=":/icons/dimensionality.png", order=0)
class CorrelationMatrixWidget(ToolboxWidgetBase):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        self.toast = None
        super().__init__(
            datatable,
            CorrelationMatrixWidgetSettings,
            title="Correlation Matrix",
            parent=parent,
        )

    def _create_toolbar_items(self, toolbar: QToolBar) -> None:
        self.variables_table_widget = VariablesTableWidget()
        self.variables_table_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.variables_table_widget.set_data(self.datatable.variables, self._settings.selected_variables)
        self.variables_table_widget.setMaximumHeight(600)
        self.variables_table_widget.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        variables_button = get_widget_tool_button(
            toolbar,
            self.variables_table_widget,
            "Variables",
            QIcon(":/icons/variables.png"),
        )
        toolbar.addWidget(variables_button)

    def _get_settings_value(self):
        return CorrelationMatrixWidgetSettings(
            self.variables_table_widget.get_selected_variable_names(),
        )

    def _update(self):
        self.report_view.clear()

        selected_variables = self.variables_table_widget.get_selected_variables_dict()

        df = self.datatable.get_df(
            list(selected_variables),
            SplitMode.ANIMAL,
            "",
        )

        result = get_correlation_matrix_result(
            self.datatable.dataset,
            df,
            list(selected_variables),
            get_figsize_from_widget(self.report_view),
        )

        self.report_view.set_content(result.report)
