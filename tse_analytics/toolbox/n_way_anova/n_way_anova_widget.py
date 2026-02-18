from dataclasses import dataclass, field

from pyqttoast import ToastPreset
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QAbstractScrollArea,
    QLabel,
    QToolBar,
    QWidget,
)

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_widget_tool_button
from tse_analytics.pipeline.enums import EFFECT_SIZE, P_ADJUSTMENT
from tse_analytics.toolbox.n_way_anova.n_way_anova_settings_widget_ui import Ui_NWayAnovaSettingsWidget
from tse_analytics.toolbox.n_way_anova.processor import get_n_way_anova_result
from tse_analytics.toolbox.toolbox_registry import toolbox_plugin
from tse_analytics.toolbox.toolbox_widget_base import ToolboxWidgetBase
from tse_analytics.views.misc.factors_table_widget import FactorsTableWidget
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class NWayAnovaWidgetSettings:
    selected_variable: str = None
    selected_factors: list[str] = field(default_factory=list)


@toolbox_plugin(category="ANOVA", label="N-way ANOVA", icon=":/icons/anova.png", order=1)
class NWayAnovaWidget(ToolboxWidgetBase):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(
            datatable,
            NWayAnovaWidgetSettings,
            title="N-way ANOVA",
            parent=parent,
        )

    def _create_toolbar_items(self, toolbar: QToolBar) -> None:
        toolbar.addWidget(QLabel("Dependent variable:"))
        self.variable_selector = VariableSelector(toolbar)
        self.variable_selector.set_data(self.datatable.variables, selected_variable=self._settings.selected_variable)
        toolbar.addWidget(self.variable_selector)

        self.factors_table_widget = FactorsTableWidget()
        self.factors_table_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.factors_table_widget.set_data(
            self.datatable.dataset.factors, selected_factors=self._settings.selected_factors
        )
        self.factors_table_widget.setMaximumHeight(400)
        self.factors_table_widget.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        factors_button = get_widget_tool_button(
            toolbar,
            self.factors_table_widget,
            "Factors",
            QIcon(":/icons/factors.png"),
        )
        toolbar.addWidget(factors_button)

        self.settings_widget = QWidget()
        self.settings_widget_ui = Ui_NWayAnovaSettingsWidget()
        self.settings_widget_ui.setupUi(self.settings_widget)
        settings_button = get_widget_tool_button(
            toolbar,
            self.settings_widget,
            "Settings",
            QIcon(":/icons/icons8-settings-16.png"),
        )
        toolbar.addWidget(settings_button)

        self.settings_widget_ui.comboBoxPAdjustment.addItems(P_ADJUSTMENT.keys())
        self.settings_widget_ui.comboBoxPAdjustment.setCurrentText("No correction")

        self.settings_widget_ui.comboBoxEffectSizeType.addItems(EFFECT_SIZE.keys())
        self.settings_widget_ui.comboBoxEffectSizeType.setCurrentText("Hedges g")

    def _get_settings_value(self):
        return NWayAnovaWidgetSettings(
            self.variable_selector.currentText(),
            self.factors_table_widget.get_selected_factor_names(),
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

        factor_names = self.factors_table_widget.get_selected_factor_names()

        if len(factor_names) < 2:
            make_toast(
                self,
                "N-way ANOVA",
                "Please select several factors.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        columns = (
            self.datatable.get_default_columns() + list(self.datatable.dataset.factors) + [dependent_variable.name]
        )
        df = self.datatable.get_filtered_df(columns)

        result = get_n_way_anova_result(
            self.datatable.dataset,
            df,
            dependent_variable,
            factor_names,
            EFFECT_SIZE[self.settings_widget_ui.comboBoxEffectSizeType.currentText()],
            P_ADJUSTMENT[self.settings_widget_ui.comboBoxPAdjustment.currentText()],
        )

        self.report_view.set_content(result.report)
