from dataclasses import dataclass

from pyqttoast import ToastPreset
from PySide6.QtWidgets import QComboBox, QLabel, QToolBar, QWidget

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_figsize_from_widget
from tse_analytics.pipeline.enums import EFFECT_SIZE
from tse_analytics.toolbox.one_way_anova.processor import get_one_way_anova_result
from tse_analytics.toolbox.toolbox_registry import toolbox_plugin
from tse_analytics.toolbox.toolbox_widget_base import ToolboxWidgetBase
from tse_analytics.views.misc.factor_selector import FactorSelector
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class OneWayAnovaWidgetSettings:
    selected_variable: str = None
    selected_factor: str = None


@toolbox_plugin(category="ANOVA", label="One-way ANOVA", icon=":/icons/anova.png", order=0)
class OneWayAnovaWidget(ToolboxWidgetBase):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(
            datatable,
            OneWayAnovaWidgetSettings,
            title="One-way ANOVA",
            parent=parent,
        )

    def _create_toolbar_items(self, toolbar: QToolBar) -> None:
        toolbar.addWidget(QLabel("Dependent variable:"))
        self.variable_selector = VariableSelector(toolbar)
        self.variable_selector.set_data(self.datatable.variables, selected_variable=self._settings.selected_variable)
        toolbar.addWidget(self.variable_selector)

        toolbar.addWidget(QLabel("Factor:"))
        self.factor_selector = FactorSelector(toolbar)
        self.factor_selector.set_data(self.datatable.dataset.factors, selected_factor=self._settings.selected_factor)
        toolbar.addWidget(self.factor_selector)

        toolbar.addWidget(QLabel("Effect size type:"))
        self.comboBoxEffectSizeType = QComboBox(toolbar)
        self.comboBoxEffectSizeType.addItems(list(EFFECT_SIZE))
        self.comboBoxEffectSizeType.setCurrentText("Hedges g")
        toolbar.addWidget(self.comboBoxEffectSizeType)

    def _get_settings_value(self):
        return OneWayAnovaWidgetSettings(
            self.variable_selector.currentText(),
            self.factor_selector.currentText(),
        )

    def _update(self):
        self.report_view.clear()

        dependent_variable = self.variable_selector.get_selected_variable()
        if dependent_variable is None:
            make_toast(
                self,
                self.title,
                "Please select dependent variable.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        factor_name = self.factor_selector.currentText()
        if factor_name == "":
            make_toast(
                self,
                self.title,
                "Please select a single factor.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        columns = (
            self.datatable.get_default_columns() + list(self.datatable.dataset.factors) + [dependent_variable.name]
        )
        df = self.datatable.get_filtered_df(columns)

        result = get_one_way_anova_result(
            self.datatable.dataset,
            df,
            dependent_variable,
            factor_name,
            EFFECT_SIZE[self.comboBoxEffectSizeType.currentText()],
            get_figsize_from_widget(self.report_view),
        )

        self.report_view.set_content(result.report)
