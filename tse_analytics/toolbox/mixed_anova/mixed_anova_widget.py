from dataclasses import dataclass

from pyqttoast import ToastPreset
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QMessageBox, QToolBar, QWidget

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import FactorRole
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
    variable: str | None = None
    between_subject_factor: str | None = None
    within_subject_factor: str | None = None


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
        self.variable_selector.set_data(self.datatable.variables, selected_variable=self._settings.variable)
        toolbar.addWidget(self.variable_selector)

        toolbar.addWidget(QLabel("Between-subject Factor:"))
        self.between_subject_factor_selector = FactorSelector(
            toolbar,
            self.datatable.dataset.factors,
            selected_factor=self._settings.between_subject_factor,
            show_role=FactorRole.BETWEEN_SUBJECT,
        )
        toolbar.addWidget(self.between_subject_factor_selector)

        toolbar.addWidget(QLabel("Within-subject Factor:"))
        self.within_subject_factor_selector = FactorSelector(
            toolbar,
            self.datatable.dataset.factors,
            selected_factor=self._settings.within_subject_factor,
            show_role=FactorRole.WITHIN_SUBJECT,
        )
        toolbar.addWidget(self.within_subject_factor_selector)

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
            self.between_subject_factor_selector.currentText(),
            self.within_subject_factor_selector.currentText(),
        )

    def _update(self):
        self.report_view.clear()

        variable = self.variable_selector.get_selected_variable()

        between_subject_factor_name = self.between_subject_factor_selector.currentText()
        if between_subject_factor_name == "":
            make_toast(
                self,
                self.title,
                "Please select a between-subject factor.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        within_subject_factor_name = self.within_subject_factor_selector.currentText()
        if within_subject_factor_name == "":
            make_toast(
                self,
                self.title,
                "Please select a within-subject factor.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        do_pairwise_tests = True
        if (
            QMessageBox.question(
                self,
                "Perform pairwise tests?",
                "Calculation of pairwise tests with many time bins can take a long time!",
            )
            == QMessageBox.StandardButton.No
        ):
            do_pairwise_tests = False

        columns = [
            self.datatable.dataset.subject_id_column,
            between_subject_factor_name,
            within_subject_factor_name,
            variable.name,
        ]
        df = self.datatable.get_filtered_df(columns)
        df.dropna(inplace=True)

        result = get_mixed_anova_result(
            self.datatable,
            variable,
            between_subject_factor_name,
            within_subject_factor_name,
            do_pairwise_tests,
            EFFECT_SIZE[self.settings_widget_ui.comboBoxEffectSizeType.currentText()],
            P_ADJUSTMENT[self.settings_widget_ui.comboBoxPAdjustment.currentText()],
            get_figsize_from_widget(self.report_view),
        )

        self.report_view.set_content(result.report)
