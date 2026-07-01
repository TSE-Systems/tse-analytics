from dataclasses import dataclass
from datetime import datetime
from functools import partial

from pyqttoast import ToastPreset
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDoubleSpinBox, QLabel, QMenu, QSpinBox, QToolBar, QToolButton, QWidget

from tse_analytics.core import manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import FactorRole
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_figsize_from_widget
from tse_analytics.core.workers.task_manager import TaskManager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.toolbox.chronobiology.processor import ChronobiologyResult, get_chronobiology_result
from tse_analytics.toolbox.toolbox_registry import toolbox_plugin
from tse_analytics.toolbox.toolbox_widget_base import ToolboxWidgetBase
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class ChronobiologyWidgetSettings:
    group_by: str = "Animal"
    selected_variable: str | None = None
    period_hours: float = 24.0
    period2_hours: float = 12.0
    bins_per_hour: int = 1
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
        self._last_result: ChronobiologyResult | None = None

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
            show_role=FactorRole.BETWEEN_SUBJECT,
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

        toolbar.addSeparator()
        self.add_datatable_button = QToolButton(toolbar)
        self.add_datatable_button.setText("Add Datatable")
        self.add_datatable_button.setIcon(QIcon(":/icons/icons8-insert-table-16.png"))
        self.add_datatable_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.add_datatable_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.add_datatable_button.setToolTip(
            "Add a result table to the dataset as a new datatable (available when grouping by Animal)"
        )
        self.add_datatable_menu = QMenu(self.add_datatable_button)
        self.add_datatable_button.setMenu(self.add_datatable_menu)
        self.add_datatable_button.setEnabled(False)
        toolbar.addWidget(self.add_datatable_button)

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

        self.update_action.setEnabled(False)

        factor_name = self.group_by_selector.currentText()

        self.toast = make_toast(self, self.title, "Processing...")
        self.toast.show()

        worker = Worker(
            get_chronobiology_result,
            self.datatable,
            variable,
            factor_name,
            period_hours=self.period_spin_box.value(),
            period2_hours=self.period2_spin_box.value(),
            bins_per_hour=self.bins_spin_box.value(),
            onset_threshold_pct=self.onset_threshold_spin_box.value(),
            figsize=get_figsize_from_widget(self.report_view),
        )
        worker.signals.result.connect(self._result)
        worker.signals.finished.connect(self._finished)
        TaskManager.start_task(worker)

    def _result(self, result: ChronobiologyResult):
        self.report_view.set_content(result.report)
        self._last_result = result

        self.add_datatable_menu.clear()
        for label in result.tables:
            action = self.add_datatable_menu.addAction(label)
            action.triggered.connect(partial(self._add_datatable, label))
        self.add_datatable_button.setEnabled(len(result.tables) > 0)

    def _finished(self):
        self.toast.hide()
        self.update_action.setEnabled(True)

    def _add_datatable(self, label: str, _checked: bool = False):
        # ``_checked`` absorbs the bool emitted by QAction.triggered (delivered to
        # the functools.partial slot).
        if self._last_result is None or label not in self._last_result.tables:
            return

        now_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        datatable = self._last_result.tables[label].to_datatable(
            self.datatable.dataset,
            f"Chronobiology {label} [{now_string}]",
        )
        manager.add_datatable(datatable)

        make_toast(
            self,
            self.title,
            f"'{label}' table added.",
            duration=2000,
            preset=ToastPreset.INFORMATION,
            show_duration_bar=True,
        ).show()
