from dataclasses import dataclass

from pyqttoast import ToastPreset
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QMessageBox, QToolBar, QWidget

from tse_analytics.core.data.binning import BinningMode
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import (
    get_figsize_from_widget,
    get_widget_tool_button,
)
from tse_analytics.pipeline.enums import EFFECT_SIZE, P_ADJUSTMENT
from tse_analytics.toolbox.mixed_anova.mixed_anova_settings_widget_ui import Ui_MixedAnovaSettingsWidget
from tse_analytics.toolbox.mixed_anova.processor import get_mixed_anova_result
from tse_analytics.toolbox.toolbox_registry import toolbox_plugin
from tse_analytics.toolbox.toolbox_widget_base import ToolboxWidgetBase
from tse_analytics.views.misc.factor_selector import FactorSelector
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class MixedAnovaWidgetSettings:
    selected_variable: str | None = None
    selected_factor: str | None = None


@toolbox_plugin(category="ANOVA", label="Mixed-design ANOVA", icon=":/icons/anova.png", order=3)
class MixedAnovaWidget(ToolboxWidgetBase):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(
            datatable,
            MixedAnovaWidgetSettings,
            title="Mixed-design ANOVA",
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

        self.settings_widget = QWidget()
        self.settings_widget_ui = Ui_MixedAnovaSettingsWidget()
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
        return MixedAnovaWidgetSettings(
            self.variable_selector.currentText(),
            self.factor_selector.currentText(),
        )

    def _update(self):
        self.report_view.clear()

        variable = self.variable_selector.get_selected_variable()
        if variable is None:
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

        do_pairwise_tests = True
        if not self.datatable.dataset.binning_settings.apply:
            make_toast(
                self,
                self.title,
                "Please apply a proper binning first.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return
        elif self.datatable.dataset.binning_settings.mode == BinningMode.INTERVALS:
            if (
                QMessageBox.question(
                    self,
                    "Perform pairwise tests?",
                    "Calculation of pairwise tests with many time bins can take a long time!",
                )
                == QMessageBox.StandardButton.No
            ):
                do_pairwise_tests = False

        df = self.datatable.get_preprocessed_df(
            variables={variable.name: variable},
            split_mode=SplitMode.ANIMAL,
            selected_factor_name=None,
            dropna=True,
        )

        result = get_mixed_anova_result(
            self.datatable.dataset,
            df,
            variable,
            factor_name,
            do_pairwise_tests,
            EFFECT_SIZE[self.settings_widget_ui.comboBoxEffectSizeType.currentText()],
            P_ADJUSTMENT[self.settings_widget_ui.comboBoxPAdjustment.currentText()],
            get_figsize_from_widget(self.report_view),
        )

        self.report_view.set_content(result.report)
