from dataclasses import dataclass

from PySide6.QtWidgets import QLabel, QToolBar, QWidget

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.utils import get_figsize_from_widget
from tse_analytics.toolbox.regression.processor import get_regression_result
from tse_analytics.toolbox.toolbox_widget_base import ToolboxWidgetBase
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class RegressionWidgetSettings:
    group_by: str = "Animal"
    covariate_variable: str | None = None
    response_variable: str | None = None


class RegressionWidget(ToolboxWidgetBase):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(
            datatable,
            RegressionWidgetSettings,
            title="Regression",
            parent=parent,
        )

    def _create_toolbar_items(self, toolbar: QToolBar) -> None:
        toolbar.addWidget(QLabel("Covariate:"))
        self.covariateVariableSelector = VariableSelector(toolbar)
        self.covariateVariableSelector.set_data(
            self.datatable.variables, selected_variable=self._settings.covariate_variable
        )
        toolbar.addWidget(self.covariateVariableSelector)

        toolbar.addWidget(QLabel("Response:"))
        self.responseVariableSelector = VariableSelector(toolbar)
        self.responseVariableSelector.set_data(
            self.datatable.variables, selected_variable=self._settings.response_variable
        )
        toolbar.addWidget(self.responseVariableSelector)

        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Group by:"))
        self.group_by_selector = GroupBySelector(toolbar, self.datatable, selected_mode=self._settings.group_by)
        toolbar.addWidget(self.group_by_selector)

    def _get_settings_value(self):
        return RegressionWidgetSettings(
            self.group_by_selector.currentText(),
            self.covariateVariableSelector.currentText(),
            self.responseVariableSelector.currentText(),
        )

    def _update(self):
        self.report_view.clear()

        split_mode, selected_factor_name = self.group_by_selector.get_group_by()

        covariate = self.covariateVariableSelector.get_selected_variable()
        response = self.responseVariableSelector.get_selected_variable()

        variable_columns = [response.name] if response.name == covariate.name else [response.name, covariate.name]
        columns = self.datatable.get_default_columns() + list(self.datatable.dataset.factors) + variable_columns
        df = self.datatable.get_filtered_df(columns)

        result = get_regression_result(
            self.datatable.dataset,
            df,
            covariate,
            response,
            split_mode,
            selected_factor_name,
            get_figsize_from_widget(self.report_view),
        )

        self.report_view.set_content(result.report)
