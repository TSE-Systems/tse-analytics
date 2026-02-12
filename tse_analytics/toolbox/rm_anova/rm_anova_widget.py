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
from tse_analytics.toolbox.rm_anova.processor import get_rm_anova_result
from tse_analytics.toolbox.rm_anova.rm_anova_settings_widget_ui import Ui_RMAnovaSettingsWidget
from tse_analytics.toolbox.toolbox_widget_base import ToolboxWidgetBase
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class RMAnovaWidgetSettings:
    group_by: str = "Animal"
    selected_variable: str = None


class RMAnovaWidget(ToolboxWidgetBase):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(
            datatable,
            RMAnovaWidgetSettings,
            title="Repeated Measures ANOVA",
            parent=parent,
        )

    def _create_toolbar_items(self, toolbar: QToolBar) -> None:
        toolbar.addWidget(QLabel("Dependent variable:"))
        self.variable_selector = VariableSelector(toolbar)
        self.variable_selector.set_data(self.datatable.variables, selected_variable=self._settings.selected_variable)
        toolbar.addWidget(self.variable_selector)

        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Group by:"))
        self.group_by_selector = GroupBySelector(
            toolbar,
            self.datatable,
            selected_mode=self._settings.group_by,
            disable_total_mode=True,
        )
        toolbar.addWidget(self.group_by_selector)

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
        return RMAnovaWidgetSettings(
            self.group_by_selector.currentText(),
            self.variable_selector.currentText(),
        )

    def _update(self):
        self.report_view.clear()

        split_mode, selected_factor_name = self.group_by_selector.get_group_by()
        variable = self.variable_selector.get_selected_variable()

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

        result = get_rm_anova_result(
            self.datatable.dataset,
            df,
            variable,
            split_mode,
            selected_factor_name,
            do_pairwise_tests,
            EFFECT_SIZE[self.settings_widget_ui.comboBoxEffectSizeType.currentText()],
            P_ADJUSTMENT[self.settings_widget_ui.comboBoxPAdjustment.currentText()],
            get_figsize_from_widget(self.report_view),
        )

        self.report_view.set_content(result.report)
