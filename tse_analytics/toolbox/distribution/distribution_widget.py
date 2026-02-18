from dataclasses import dataclass

from PySide6.QtWidgets import QCheckBox, QComboBox, QLabel, QToolBar, QWidget

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.utils import get_figsize_from_widget
from tse_analytics.toolbox.distribution.processor import get_distribution_result
from tse_analytics.toolbox.toolbox_registry import toolbox_plugin
from tse_analytics.toolbox.toolbox_widget_base import ToolboxWidgetBase
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class DistributionWidgetSettings:
    group_by: str = "Animal"
    selected_variable: str | None = None
    show_points: bool = False
    plot_type: str = "Violin plot"


@toolbox_plugin(category="Exploration", label="Distribution", icon=":/icons/exploration.png", order=1)
class DistributionWidget(ToolboxWidgetBase):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(
            datatable,
            DistributionWidgetSettings,
            title="Distribution",
            parent=parent,
        )

    def _create_toolbar_items(self, toolbar: QToolBar) -> None:
        self.variableSelector = VariableSelector(toolbar)
        self.variableSelector.set_data(self.datatable.variables, selected_variable=self._settings.selected_variable)
        toolbar.addWidget(self.variableSelector)

        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Group by:"))
        self.group_by_selector = GroupBySelector(toolbar, self.datatable, selected_mode=self._settings.group_by)
        toolbar.addWidget(self.group_by_selector)

        self.plot_type_combobox = QComboBox(toolbar)
        self.plot_type_combobox.addItems(["Violin plot", "Box plot", "Raincloud plot"])
        self.plot_type_combobox.setCurrentText(self._settings.plot_type)
        toolbar.addWidget(self.plot_type_combobox)

        self.checkBoxShowPoints = QCheckBox("Show Points", toolbar)
        self.checkBoxShowPoints.setChecked(self._settings.show_points)
        toolbar.addWidget(self.checkBoxShowPoints)

    def _get_settings_value(self):
        return DistributionWidgetSettings(
            self.group_by_selector.currentText(),
            self.variableSelector.currentText(),
            self.checkBoxShowPoints.isChecked(),
            self.plot_type_combobox.currentText(),
        )

    def _update(self):
        self.report_view.clear()

        split_mode, selected_factor_name = self.group_by_selector.get_group_by()
        variable = self.variableSelector.get_selected_variable()

        df = self.datatable.get_df(
            [variable.name],
            split_mode,
            selected_factor_name,
        )

        result = get_distribution_result(
            self.datatable.dataset,
            df,
            variable.name,
            split_mode,
            selected_factor_name,
            self.plot_type_combobox.currentText(),
            self.checkBoxShowPoints.isChecked(),
            get_figsize_from_widget(self.report_view),
        )

        self.report_view.set_content(result.report)
