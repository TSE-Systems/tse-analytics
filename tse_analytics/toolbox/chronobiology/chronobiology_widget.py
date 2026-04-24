from dataclasses import dataclass

from PySide6.QtWidgets import QDoubleSpinBox, QLabel, QSpinBox, QToolBar, QWidget

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.utils import get_figsize_from_widget
from tse_analytics.toolbox.chronobiology.processor import get_chronobiology_result
from tse_analytics.toolbox.toolbox_registry import toolbox_plugin
from tse_analytics.toolbox.toolbox_widget_base import ToolboxWidgetBase
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class ChronobiologyWidgetSettings:
    group_by: str = "Animal"
    selected_variable: str = None
    period_hours: float = 24.0
    period2_hours: float = 12.0
    bins_per_hour: int = 6
    onset_threshold_pct: float = 50.0


@toolbox_plugin(
    category="Chronobiology",
    label="Chronobiology",
    icon=":/icons/icons8-normal-distribution-histogram-16.png",
    order=0,
)
class ChronobiologyWidget(ToolboxWidgetBase):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(
            datatable,
            ChronobiologyWidgetSettings,
            title="Chronobiology",
            parent=parent,
        )

    def _create_toolbar_items(self, toolbar: QToolBar) -> None:
        self.variableSelector = VariableSelector(toolbar)
        self.variableSelector.set_data(self.datatable.variables, selected_variable=self._settings.selected_variable)
        toolbar.addWidget(self.variableSelector)

        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Group by:"))
        self.group_by_selector = GroupBySelector(
            toolbar,
            self.datatable,
            selected_mode=self._settings.group_by,
        )
        toolbar.addWidget(self.group_by_selector)

        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Period (h):"))
        self.period_spin_box = QDoubleSpinBox(
            toolbar,
            minimum=1.0,
            maximum=72.0,
            singleStep=0.5,
            decimals=2,
            value=self._settings.period_hours,
        )
        toolbar.addWidget(self.period_spin_box)

        toolbar.addWidget(QLabel("Harmonic period (h):"))
        self.period2_spin_box = QDoubleSpinBox(
            toolbar,
            minimum=0.5,
            maximum=72.0,
            singleStep=0.5,
            decimals=2,
            value=self._settings.period2_hours,
        )
        toolbar.addWidget(self.period2_spin_box)

        toolbar.addWidget(QLabel("Bins/hour:"))
        self.bins_spin_box = QSpinBox(
            toolbar,
            minimum=1,
            maximum=60,
            singleStep=1,
            value=self._settings.bins_per_hour,
        )
        toolbar.addWidget(self.bins_spin_box)

        toolbar.addWidget(QLabel("Onset threshold %:"))
        self.onset_threshold_spin_box = QDoubleSpinBox(
            toolbar,
            minimum=1.0,
            maximum=99.0,
            singleStep=5.0,
            decimals=1,
            value=self._settings.onset_threshold_pct,
        )
        toolbar.addWidget(self.onset_threshold_spin_box)

    def _get_settings_value(self):
        return ChronobiologyWidgetSettings(
            self.group_by_selector.currentText(),
            self.variableSelector.currentText(),
            self.period_spin_box.value(),
            self.period2_spin_box.value(),
            self.bins_spin_box.value(),
            self.onset_threshold_spin_box.value(),
        )

    def _update(self):
        self.report_view.clear()

        grouping_settings = self.group_by_selector.get_grouping_settings()
        variable = self.variableSelector.get_selected_variable()

        columns = self.datatable.get_default_columns() + list(self.datatable.dataset.factors) + [variable.name]
        df = self.datatable.get_filtered_df(columns)
        df = df.dropna()

        result = get_chronobiology_result(
            self.datatable,
            df,
            variable,
            grouping_settings,
            period_hours=self.period_spin_box.value(),
            period2_hours=self.period2_spin_box.value(),
            bins_per_hour=self.bins_spin_box.value(),
            onset_threshold_pct=self.onset_threshold_spin_box.value(),
            figsize=get_figsize_from_widget(self.report_view),
        )

        self.report_view.set_content(result.report)
