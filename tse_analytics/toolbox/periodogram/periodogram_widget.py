from dataclasses import dataclass

from pyqttoast import ToastPreset
from PySide6.QtWidgets import QDoubleSpinBox, QLabel, QToolBar, QWidget

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_figsize_from_widget
from tse_analytics.core.workers.task_manager import TaskManager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.toolbox.periodogram.processor import (
    MAX_PERIOD_HOURS,
    MIN_PERIOD_HOURS,
    PeriodogramResult,
    get_periodogram_result,
)
from tse_analytics.toolbox.toolbox_registry import toolbox_plugin
from tse_analytics.toolbox.toolbox_widget_base import ToolboxWidgetBase
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class PeriodogramWidgetSettings:
    group_by: str = "Animal"
    selected_variable: str | None = None
    min_period: float = MIN_PERIOD_HOURS
    max_period: float = MAX_PERIOD_HOURS


@toolbox_plugin(
    category="Chronobiology",
    label="Periodogram",
    icon=":/icons/icons8-normal-distribution-histogram-16.png",
    order=2,
)
class PeriodogramWidget(ToolboxWidgetBase):
    """Lomb–Scargle periodogram of a selected variable, one power curve per group level."""

    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(
            datatable,
            PeriodogramWidgetSettings,
            title="Periodogram",
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
        toolbar.addWidget(QLabel("Min period (h):"))
        self.min_period_spin_box = QDoubleSpinBox(
            toolbar,
            minimum=0.5,
            maximum=240.0,
            singleStep=1.0,
            decimals=1,
            value=self._settings.min_period,
        )
        toolbar.addWidget(self.min_period_spin_box)

        toolbar.addWidget(QLabel("Max period (h):"))
        self.max_period_spin_box = QDoubleSpinBox(
            toolbar,
            minimum=1.0,
            maximum=480.0,
            singleStep=1.0,
            decimals=1,
            value=self._settings.max_period,
        )
        toolbar.addWidget(self.max_period_spin_box)

    def _get_settings_value(self):
        return PeriodogramWidgetSettings(
            self.group_by_selector.currentText(),
            self.variableSelector.currentText(),
            self.min_period_spin_box.value(),
            self.max_period_spin_box.value(),
        )

    def _update(self):
        self.report_view.clear()

        variable = self.variableSelector.get_selected_variable()
        if variable is None:
            make_toast(
                self,
                self.title,
                "Please select a variable.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        min_period = self.min_period_spin_box.value()
        max_period = self.max_period_spin_box.value()
        if min_period >= max_period:
            make_toast(
                self,
                self.title,
                "Min period must be smaller than max period.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        factor_name = self.group_by_selector.currentText()

        self.update_action.setEnabled(False)

        self.toast = make_toast(self, self.title, "Processing...")
        self.toast.show()

        worker = Worker(
            get_periodogram_result,
            self.datatable,
            variable,
            factor_name,
            min_period,
            max_period,
            get_figsize_from_widget(self.report_view),
        )
        worker.signals.result.connect(self._result)
        worker.signals.finished.connect(self._finished)
        TaskManager.start_task(worker)

    def _result(self, result: PeriodogramResult):
        self.report_view.set_content(result.report)

    def _finished(self):
        self.toast.hide()
        self.update_action.setEnabled(True)
