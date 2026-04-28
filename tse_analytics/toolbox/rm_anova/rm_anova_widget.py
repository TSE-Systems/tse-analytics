from dataclasses import dataclass, field

from pyqttoast import ToastPreset
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QMessageBox, QToolBar, QWidget

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import FactorKind
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import (
    get_figsize_from_widget,
    get_widget_tool_button,
)
from tse_analytics.pipeline.enums import EFFECT_SIZE, P_ADJUSTMENT
from tse_analytics.toolbox.rm_anova.processor import get_rm_anova_result
from tse_analytics.toolbox.rm_anova.rm_anova_settings_widget_ui import Ui_RMAnovaSettingsWidget
from tse_analytics.toolbox.toolbox_registry import toolbox_plugin
from tse_analytics.toolbox.toolbox_widget_base import ToolboxWidgetBase
from tse_analytics.views.misc.factors_table_widget import FactorsTableWidget
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class RepeatedAnovaWidgetSettings:
    selected_variable: str = None
    selected_factors: list[str] = field(default_factory=list)


@toolbox_plugin(category="ANOVA", label="Repeated Measures ANOVA", icon=":/icons/anova.png", order=2)
class RMAnovaWidget(ToolboxWidgetBase):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(
            datatable,
            RepeatedAnovaWidgetSettings,
            title="Repeated Measures ANOVA",
            parent=parent,
        )

    def _create_toolbar_items(self, toolbar: QToolBar) -> None:
        toolbar.addWidget(QLabel("Dependent variable:"))
        self.variable_selector = VariableSelector(toolbar)
        self.variable_selector.set_data(self.datatable.variables, selected_variable=self._settings.selected_variable)
        toolbar.addWidget(self.variable_selector)

        show_bins = self.datatable.df["Bin"].nunique() if "Bin" in self.datatable.df.columns else None
        self.factors_table_widget = FactorsTableWidget(
            self.datatable.dataset.factors,
            selected_factors=self._settings.selected_factors,
            show_factor_kind=[FactorKind.LIGHT_CYCLES, FactorKind.TIME_PHASES],
            show_bins=show_bins,
        )
        factors_button = get_widget_tool_button(
            toolbar,
            self.factors_table_widget,
            "Within-subject Factors",
            QIcon(":/icons/factors.png"),
        )
        toolbar.addWidget(factors_button)

        self.settings_widget = QWidget()
        self.settings_widget_ui = Ui_RMAnovaSettingsWidget()
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
        return RepeatedAnovaWidgetSettings(
            self.variable_selector.currentText(),
            self.factors_table_widget.get_selected_factor_names(),
        )

    def _update(self):
        self.report_view.clear()

        dependent_variable = self.variable_selector.get_selected_variable()
        factor_names = self.factors_table_widget.get_selected_factor_names()

        do_pairwise_tests = True
        if len(factor_names) == 0:
            make_toast(
                self,
                self.title,
                "Please select one or two within-subject factor(s) first.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return
        elif len(factor_names) > 2:
            make_toast(
                self,
                self.title,
                "Repeated measures ANOVA with three or more factors is not supported.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return
        elif "Bin" in factor_names:
            if (
                QMessageBox.question(
                    self,
                    "Perform pairwise tests?",
                    "Calculation of pairwise tests with many time bins can take a long time!",
                )
                == QMessageBox.StandardButton.No
            ):
                do_pairwise_tests = False

        result = get_rm_anova_result(
            self.datatable,
            dependent_variable,
            factor_names,
            do_pairwise_tests,
            EFFECT_SIZE[self.settings_widget_ui.comboBoxEffectSizeType.currentText()],
            P_ADJUSTMENT[self.settings_widget_ui.comboBoxPAdjustment.currentText()],
            get_figsize_from_widget(self.report_view),
        )

        self.report_view.set_content(result.report)
