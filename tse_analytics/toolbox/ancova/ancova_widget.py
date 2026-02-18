from dataclasses import dataclass

from pyqttoast import ToastPreset
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QToolBar, QWidget

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_widget_tool_button
from tse_analytics.pipeline.enums import EFFECT_SIZE, P_ADJUSTMENT
from tse_analytics.toolbox.ancova.ancova_settings_widget_ui import Ui_AncovaSettingsWidget
from tse_analytics.toolbox.ancova.processor import get_ancova_result
from tse_analytics.toolbox.toolbox_registry import toolbox_plugin
from tse_analytics.toolbox.toolbox_widget_base import ToolboxWidgetBase
from tse_analytics.views.misc.factor_selector import FactorSelector
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class AncovaWidgetSettings:
    selected_variable: str | None = None
    selected_covariate: str | None = None
    selected_factor: str | None = None


@toolbox_plugin(category="ANOVA", label="ANCOVA", icon=":/icons/anova.png", order=4)
class AncovaWidget(ToolboxWidgetBase):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(
            datatable,
            AncovaWidgetSettings,
            title="ANCOVA",
            parent=parent,
        )

    def _create_toolbar_items(self, toolbar: QToolBar) -> None:
        toolbar.addWidget(QLabel("Dependent variable:"))
        self.variable_selector = VariableSelector(toolbar)
        self.variable_selector.set_data(self.datatable.variables, selected_variable=self._settings.selected_variable)
        toolbar.addWidget(self.variable_selector)

        toolbar.addWidget(QLabel("Covariate variable:"))
        self.covariate_selector = VariableSelector(toolbar)
        self.covariate_selector.set_data(self.datatable.variables, selected_variable=self._settings.selected_covariate)
        toolbar.addWidget(self.covariate_selector)

        toolbar.addWidget(QLabel("Factor:"))
        self.factor_selector = FactorSelector(toolbar)
        self.factor_selector.set_data(self.datatable.dataset.factors, selected_factor=self._settings.selected_factor)
        toolbar.addWidget(self.factor_selector)

        self.settings_widget = QWidget()
        self.settings_widget_ui = Ui_AncovaSettingsWidget()
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
        return AncovaWidgetSettings(
            self.variable_selector.currentText(),
            self.covariate_selector.currentText(),
            self.factor_selector.currentText(),
        )

    def _update(self):
        self.report_view.clear()

        dependent_variable = self.variable_selector.get_selected_variable()
        selected_covariate = self.covariate_selector.get_selected_variable()

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
            self.datatable.get_default_columns()
            + list(self.datatable.dataset.factors)
            + [dependent_variable.name, selected_covariate.name]
        )
        df = self.datatable.get_filtered_df(columns)

        result = get_ancova_result(
            self.datatable.dataset,
            df,
            dependent_variable,
            selected_covariate,
            factor_name,
            EFFECT_SIZE[self.settings_widget_ui.comboBoxEffectSizeType.currentText()],
            P_ADJUSTMENT[self.settings_widget_ui.comboBoxPAdjustment.currentText()],
        )

        self.report_view.set_content(result.report)
