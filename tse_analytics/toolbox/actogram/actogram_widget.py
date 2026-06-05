from dataclasses import dataclass

from pyqttoast import ToastPreset
from PySide6.QtWidgets import QLabel, QSpinBox, QToolBar, QWidget

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_figsize_from_widget
from tse_analytics.core.workers.task_manager import TaskManager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.toolbox.actogram.processor import ActogramResult, get_actogram_result
from tse_analytics.toolbox.toolbox_registry import toolbox_plugin
from tse_analytics.toolbox.toolbox_widget_base import ToolboxWidgetBase
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class ActogramWidgetSettings:
    variable: str | None = None
    bins_per_hour: int = 6


@toolbox_plugin(category="Chronobiology", label="Actogram", icon=":/icons/icons8-barcode-16.png", order=1)
class ActogramWidget(ToolboxWidgetBase):
    """Widget for visualizing activity patterns over time in a double-plotted actogram format.

    An actogram is a graphical representation of activity data over multiple days,
    typically used in chronobiology to visualize circadian rhythms. This widget
    creates a double-plotted actogram where each row represents two consecutive days,
    allowing for better visualization of activity patterns that cross midnight.
    One actogram is rendered per animal.
    """

    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(
            datatable,
            ActogramWidgetSettings,
            title="Actogram",
            parent=parent,
        )

    def _create_toolbar_items(self, toolbar: QToolBar) -> None:
        self.variableSelector = VariableSelector(toolbar)
        self.variableSelector.set_data(self.datatable.variables, selected_variable=self._settings.variable)
        toolbar.addWidget(self.variableSelector)

        toolbar.addWidget(QLabel("Bins per hour:"))
        self.bins_spin_box = QSpinBox(
            toolbar,
            minimum=1,
            maximum=60,
            singleStep=1,
            value=self._settings.bins_per_hour,
        )
        toolbar.addWidget(self.bins_spin_box)

    def _get_settings_value(self):
        return ActogramWidgetSettings(
            self.variableSelector.currentText(),
            self.bins_spin_box.value(),
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

        self.toast = make_toast(self, self.title, "Processing...")
        self.toast.show()

        worker = Worker(
            get_actogram_result,
            self.datatable,
            variable,
            self.bins_spin_box.value(),
            get_figsize_from_widget(self.report_view),
        )
        worker.signals.result.connect(self._result)
        worker.signals.finished.connect(self._finished)
        TaskManager.start_task(worker)

    def _result(self, result: ActogramResult):
        self.report_view.set_content(result.report)

    def _finished(self):
        self.toast.hide()
        self.update_action.setEnabled(True)
