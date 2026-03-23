from dataclasses import dataclass

from PySide6.QtWidgets import QToolBar, QWidget

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_figsize_from_widget
from tse_analytics.core.workers import TaskManager, Worker
from tse_analytics.modules.intellicage.toolbox.transitions.processor import (
    IntelliCageTransitionsResult,
    get_intellicage_transitions_result,
)
from tse_analytics.toolbox.toolbox_registry import toolbox_plugin
from tse_analytics.toolbox.toolbox_widget_base import ToolboxWidgetBase


@dataclass
class TransitionsWidgetSettings:
    alpha: float = 0.05


@toolbox_plugin(
    category="IntelliCage", label="Transitions", icon=":/icons/icons8-transition-both-directions-16.png", order=0
)
class TransitionsWidget(ToolboxWidgetBase):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(
            datatable,
            TransitionsWidgetSettings,
            "Transitions",
            parent,
        )

    def _create_toolbar_items(self, toolbar: QToolBar) -> None:
        pass

    def _get_settings_value(self):
        return TransitionsWidgetSettings(
            0.05,
        )

    def _update(self):
        self.report_view.clear()

        self.update_action.setEnabled(False)

        self.toast = make_toast(self, self.title, "Processing...")
        self.toast.show()

        columns = ["Timedelta", "Animal", "Corner"]
        df = self.datatable.df[columns]

        animal_ids = [animal.id for animal in self.datatable.dataset.animals.values() if animal.enabled]

        worker = Worker(
            get_intellicage_transitions_result,
            self.datatable.dataset,
            df,
            animal_ids,
            0.05,
            get_figsize_from_widget(self.report_view),
        )
        worker.signals.result.connect(self._result)
        worker.signals.finished.connect(self._finished)
        TaskManager.start_task(worker)

    def _result(self, result: IntelliCageTransitionsResult):
        self.report_view.set_content(result.report)

    def _finished(self):
        self.toast.hide()
        self.update_action.setEnabled(True)
