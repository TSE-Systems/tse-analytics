from dataclasses import dataclass

from PySide6.QtWidgets import QLabel, QToolBar, QWidget

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.utils import get_figsize_from_widget
from tse_analytics.toolbox.periodogram.processor import get_periodogram_result
from tse_analytics.toolbox.toolbox_widget_base import ToolboxWidgetBase
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class PeriodogramWidgetSettings:
    group_by: str = "Animal"
    selected_variable: str = None


class PeriodogramWidget(ToolboxWidgetBase):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(
            datatable,
            PeriodogramWidgetSettings,
            title="Periodogram",
            parent=parent,
        )

    def _create_toolbar_items(self, toolbar: QToolBar) -> None:
        self.variableSelector = VariableSelector(toolbar)
        self.variableSelector.set_data(self.datatable.variables, selected_variable=self._settings.selected_variable)
        toolbar.addWidget(self.variableSelector)

        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Group by:"))
        self.group_by_selector = GroupBySelector(
            toolbar, self.datatable, check_binning=True, selected_mode=self._settings.group_by
        )
        toolbar.addWidget(self.group_by_selector)

    def _get_settings_value(self):
        return PeriodogramWidgetSettings(
            self.group_by_selector.currentText(),
            self.variableSelector.currentText(),
        )

    def _update(self):
        self.report_view.clear()

        split_mode, selected_factor_name = self.group_by_selector.get_group_by()

        variable = self.variableSelector.get_selected_variable()

        df = self.datatable.get_preprocessed_df(
            variables={variable.name: variable},
            split_mode=split_mode,
            selected_factor_name=selected_factor_name,
            dropna=True,
        )

        result = get_periodogram_result(
            df,
            variable,
            get_figsize_from_widget(self.report_view),
        )

        self.report_view.set_content(result.report)
